from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'meals'
urlpatterns = [
    path('mealsList', views.meals, name='index'),
    path('mealsEdit', views.edit_meals, name='edit_meals'),
    path('mealsEdit/add_meal/<meal_option_id>', views.add_meal, name='add_meal'),
    path('mealsEdit/add_meal_option', views.add_meal_option, name='add_meal_option'),
]