import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView

from cars import forms
from cars.forms import CarForm
from cars.models import Car
from myproject.settings import BASE_DIR


def cars_home(request):
    user_cars = Car.objects.filter(user=request.user, sold=False)
    user_sold_cars = Car.objects.filter(user=request.user, sold=True)
    new_car_form = CarForm(request.POST)
    context = {
        'user_cars': user_cars,
        'form': new_car_form,
        'user_sold_cars': user_sold_cars
    }
    return render(request, 'cars/home.html', context)


def car_details(request, car_id):
    car = Car.objects.filter(pk=car_id, user=request.user)
    form = CarForm(request.POST, request.FILES, )
    context = {
        'car': car,
        'form': form,
    }
    return render(request, 'cars/car_details.html', context)



class CarUpdate(UpdateView):
    model = Car
    form_class = CarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.object.pk
        context['car'] = Car.objects.filter(pk=pk)
        return context

    def get_success_url(self):
        pk = self.object.pk
        print('##############',self.object.image)
        return '{}'.format(reverse('cars:car_details', kwargs={'car_id': pk}))


    template_name = 'cars/car_edit.html'
    # success_url = redirect('cars:car_details', Car.pk)


def add_new_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()
            location = os.path.join(BASE_DIR, 'media', 'user_uploads',
                                    '{}-{}'.format(request.user.id, request.user.username),
                                    '{}-{}'.format(car.pk, car.name), 'images')
            location_to_database = os.path.join('user_uploads',
                                    '{}-{}'.format(request.user.id, request.user.username),
                                    '{}-{}'.format(car.pk, car.name), 'images', )
            fs = FileSystemStorage(location=location)
            image = request.FILES.get('image', False)
            logo = request.FILES.get('logo', False)
            if image:
                fs.save(str(car.image), image)
                car.image = os.path.join(location_to_database, str(car.image))
                car.save()
            if logo:
                fs.save(str(car.logo), logo)
                car.logo = os.path.join(location_to_database, str(car.logo))
                car.save()


            return redirect('cars:cars_home')
    else:
        form = forms.CarForm()
    return redirect('cars:cars_home')