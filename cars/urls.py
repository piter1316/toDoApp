from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'cars'
urlpatterns = [
    path('cars', views.cars_home, name='cars_home'),
    path('cars/addCar', views.add_new_car, name='add_new_car'),
    path('cars/carDetails/<car_id>', views.car_details, name='car_details'),
    path('cars/carDetails/<pk>/edit', views.CarUpdate.as_view(), name='car_edit'),

]