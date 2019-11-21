from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'meals'
urlpatterns = [
    path('meals', views.meals, name='index'),
]