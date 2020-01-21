from django.shortcuts import render


# Create your views here.
from cars.models import Car


def cars_home(request):
    user_cars = Car.objects.filter(user=request.user)
    context = {
        'user_cars': user_cars
    }
    return render(request, 'cars/home.html', context)


def car_details(request, car_id):
    car = Car.objects.filter(pk=car_id, user=request.user)
    context = {
        'car': car
    }
    return render(request, 'cars/car_details.html', context)