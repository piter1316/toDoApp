from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'cars'
urlpatterns = [
    path('cars', views.cars_home, name='cars_home'),
    path('cars/addCar', views.add_new_car, name='add_new_car'),
    path('cars/carDetails/<car_id>', views.car_details, name='car_details'),
    path('cars/carDetails/<pk>/edit', views.CarUpdate.as_view(), name='car_edit'),
    path('cars/carDetails/<pk>/addService', views.add_service_form, name='add_service_form'),
    path('cars/carDetails/<pk>/add_fuel_fill', views.add_fuel_fill, name='add_fuel_fill'),
    path('cars/carDetails/<pk>/delete_fuel_fill', views.delete_fuel_fill, name='delete_fuel_fill'),

]