from django.shortcuts import render

from cars.models import Car, Fuel


# Create your views here.
def trip_planner(request):
    car_avg_dict = {}
    if request.user.is_authenticated:
        cars = Car.objects.filter(user=request.user.pk)
        for car in cars:
            try:
                fuels = Fuel.objects.filter(car_id=car.pk)
                fuel_liters = [fuel.liters for fuel in fuels]
                fuel_kilometers = [fuel.kilometers for fuel in fuels]
                avg = sum(fuel_liters) / sum(fuel_kilometers) * 100
                if avg:
                    car_avg_dict[car.name] = avg
            except:
                pass
    context = {'car_avg_dict': car_avg_dict}
    return render(request, 'trip_planner/trip_planner.html', context)
