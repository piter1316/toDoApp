from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView

from cars import forms
from cars.forms import NewCarForm, UpdateCar
from cars.models import Car


def cars_home(request):
    user_cars = Car.objects.filter(user=request.user)
    new_car_form = NewCarForm(request.POST)
    context = {
        'user_cars': user_cars,
        'new_car_form': new_car_form
    }
    return render(request, 'cars/home.html', context)


def car_details(request, car_id):
    car = Car.objects.filter(pk=car_id, user=request.user)
    form = UpdateCar(request.POST, request.FILES, )
    context = {
        'car': car,
        'new_car_form': form,
    }
    return render(request, 'cars/car_details.html', context)


class CarUpdate(UpdateView):
    model = Car
    form_class = UpdateCar

    def get_success_url(self):
        pk = self.object.pk
        return '{}'.format(reverse('cars:car_details', kwargs={'car_id': pk}))


    template_name = 'cars/car_edit.html'
    # success_url = redirect('cars:car_details', Car.pk)

# def add_new_car(request):
#     print('new car')
#     name = request.POST['name']
#     make = request.POST['make']
#     model = request.POST['model']
#     year = request.POST.get('year', False)
#     engine = request.POST['engine']
#     power = request.POST.get('power', False)
#     milage = request.POST.get('milage', False)
#     logo = request.FILES.get('logo', False)
#     image = request.FILES.get('image', False)
#
#     if not year:
#         year = None
#     if not power:
#         power = None
#     if not milage:
#         milage = None
#     if not logo:
#         logo = None
#     if not image:
#         image = None
#
#     new_car = Car(user=request.user, name=name, make=make,
#                   model=model, year=year, engine=engine,
#                   power=power, milage=milage, logo=logo,
#                   image=image)
#     new_car.save()
#     return redirect('cars:cars_home')

def add_new_car(request):
    if request.method == 'POST':
        form = NewCarForm(request.POST, request.FILES, )
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()
            return redirect('cars:cars_home')
    else:
        form = forms.NewCarForm()
    return redirect('cars:cars_home')