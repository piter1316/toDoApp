import json
import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView

from cars import forms
from cars.forms import CarForm, FuelFillForm
from cars.models import Car, Fuel
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
    form = CarForm(request.POST, request.FILES)
    car_fuel_fill_list = Fuel.objects.filter(car_id=car_id).order_by('-date')
    car_fill_form = FuelFillForm()
    chart_dates = Fuel.objects.filter(car_id=car_id).values('date').order_by('date')
    chart_dates_list = []
    for date in chart_dates:
        chart_dates_list.append(str(date['date']))

    context = {
        'car': car,
        'form': form,
        'car_fuel_fill_list': car_fuel_fill_list,
        'car_fill_form': car_fill_form,
        'chart_dates': str(chart_dates_list).replace('[','').replace(']','')
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
        location = os.path.join(BASE_DIR, 'media', 'user_uploads',
                                '{}-{}'.format(self.object.user.id, self.object.user),
                                '{}-{}'.format(self.object.pk, self.object.name), 'images')
        location_to_database = os.path.join('user_uploads',
                                            '{}-{}'.format(self.object.user.id, self.object.user),
                                            '{}-{}'.format(self.object.pk, self.object.name), 'images')
        fs = FileSystemStorage(location=location)
        image = self.object.image
        logo = self.object.logo
        if image:
            fs.save(str(self.object.image), image)
            self.object.image = os.path.join(location_to_database, str(self.object.image))
            self.object.save()
        if logo:
            fs.save(str(self.object.logo), logo)
            self.object.logo = os.path.join(location_to_database, str(self.object.logo))
            self.object.save()

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


def add_fuel_fill(request, pk):
    if request.method == 'POST':
        form = FuelFillForm(request.POST, request.FILES)
        car = get_object_or_404(Car, pk=pk)
        print(request.POST)

        filling = form.save(commit=False)
        filling.car_id = car
        filling.save()

        return HttpResponse('')


def delete_fuel_fill(request, pk):
    Fuel.objects.filter(pk=pk).delete()
    print(pk + 'deleted')
    return HttpResponse('')