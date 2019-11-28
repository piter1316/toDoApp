from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'meals'
urlpatterns = [
    path('mealsList', views.meals, name='index'),
    path('mealsList/update', views.update_meals_list, name='update_meals_list'),
    path('mealsList/generate_meals_list', views.generate_meals_list, name='generate_meals_list'),
    path('mealsEdit', views.edit_meals, name='edit_meals'),
    path('mealsEdit/add_meal/<meal_option_id>', views.add_meal, name='add_meal'),
    path('mealsEdit/add_meal_option', views.add_meal_option, name='add_meal_option'),
    path('mealsEdit/delete_meal_option/<meal_option_id>', views.delete_meal_option, name='delete_meal_option'),
    path('mealsEdit/edit_meal/<meal_id>', views.edit_meal, name='edit_meal'),
]