from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'meals'
urlpatterns = [
    path('mealsList', views.meals, name='index'),
    path('mealsList/<current>', views.meals, name='index'),
    path('mealsList/1/purge_meals_list', views.purge_meals_list, name='purge_meals_list'),
    path('mealsList/1/delete_selected_days', views.delete_selected_days, name='delete_selected_days'),
    path('mealsList/1/update', views.update_meals_list, name='update_meals_list'),
    path('mealsList/1/generate_meals_list', views.generate_meals_list, name='generate_meals_list'),
    path('mealsList/1/generate_shopping_lists', views.generate_shopping_lists, name='generate_shopping_lists'),
    path('mealsEdit', views.edit_meals, name='edit_meals'),
    path('ingredientsEdit', views.edit_ingredients, name='edit_ingredients'),
    path('ingredientsEdit/addShop', views.add_shop, name='add_shop'),
    path('ingredientsEdit/deleteShop/<shop_id>', views.delete_shop, name='delete_shop'),
    path('ingredientsEdit/editShop', views.edit_shop, name='edit_shop'),
    path('ingredientsEdit/newIngredient', views.new_ingredient, name='new_ingredient'),
    path('ingredientsEdit/deleteIngredient/<ingr_id>', views.delete_ingr, name='delete_ingr'),
    path('ingredientsEdit/editIngredient/<ingr_id>', views.edit_ingredient, name='edit_ingredient'),
    path('mealsEdit/add_meal/<meal_option_id>', views.add_meal, name='add_meal'),
    path('mealsEdit/delete_meal/<meal_id>', views.delete_meal, name='delete_meal'),
    path('mealsEdit/update_meal_name/<meal_id>', views.update_meal_name, name='update_meal_name'),
    path('mealsEdit/add_meal_option', views.add_meal_option, name='add_meal_option'),
    path('mealsEdit/delete_meal_option/<meal_option_id>', views.delete_meal_option, name='delete_meal_option'),
    path('mealsEdit/update_meal_option/<meal_option_id>', views.update_meal_option, name='update_meal_option'),
    path('mealsEdit/edit_meal_ingredients/<meal_id>', views.edit_meal_ingredients, name='edit_meal_ingredients'),
    path('mealsEdit/add_ingredient/<meal_id>', views.add_ingredient, name='add_ingredient'),
    path('mealsEdit/add_recipe/<meal_id>', views.add_recipe, name='add_recipe'),
    path('mealsEdit/update_ingredient/<meal_id>/<ingredient_id>', views.update_ingredient, name='update_ingredient'),
    path('mealsEdit/delete_ingredient/<meal_id>/<ingredient_id>', views.delete_ingredient, name='delete_ingredient'),
]