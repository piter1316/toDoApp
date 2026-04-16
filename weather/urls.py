from django.urls import path
from . import views


app_name = 'weather'

urlpatterns = [
    path('', views.weather_dashboard, name='weather_dashboard'),
    path('update-weather/', views.update_weather_data, name='update_weather_data'),
]