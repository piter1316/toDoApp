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
    path('mealsList/1/edit_extras/', views.edit_extras, name='edit_extras'),
    path('mealsList/1/delete_extras/<meals_list_id>', views.delete_extras, name='delete_extras'),
    path('mealsEdit', views.edit_meals, name='edit_meals'),
    path('ingredientsEdit', views.edit_ingredients, name='edit_ingredients'),
    path('ingredientsEdit/addShop', views.add_shop, name='add_shop'),
    path('ingredientsEdit/deleteShop/<shop_id>', views.delete_shop, name='delete_shop'),
    path('ingredientsEdit/editShop', views.edit_shop, name='edit_shop'),
    path('ingredientsEdit/newIngredient', views.new_ingredient, name='new_ingredient'),
    path('ingredientsEdit/deleteIngredient/<ingr_id>', views.delete_ingr, name='delete_ingr'),
    path('ingredientsEdit/editIngredient/<ingr_id>', views.edit_ingredient, name='edit_ingredient'),
    path('ingredientEdit/<ingr_id>', views.edit_ingredient_index, name='edit_ingredient_index'),
    path('ingredientsEdit/addNewDivision', views.add_new_division, name='add_new_division'),
    path('ingredientsEdit/deleteDivision/<division_id>', views.delete_division, name='delete_division'),
    path('ingredientsEdit/editDivision/<division_id>', views.edit_division, name='edit_division'),
    path('ingredientsEdit/editDivisionPriority/<division_id>', views.edit_division_priority,
         name='edit_division_priority'),
    path('mealsEdit/add_meal/<meal_option_id>', views.add_meal, name='add_meal'),
    path('mealsEdit/delete_meal/<meal_id>', views.delete_meal, name='delete_meal'),
    path('mealsEdit/update_meal_name/<meal_id>', views.update_meal_name, name='update_meal_name'),
    path('mealsEdit/copy_meal/<meal_id>', views.copy_meal, name='copy_meal'),
    path('mealsEdit/add_meal_option', views.add_meal_option, name='add_meal_option'),
    path('mealsEdit/delete_meal_option/<meal_option_id>', views.delete_meal_option, name='delete_meal_option'),
    path('mealsEdit/update_meal_option/<meal_option_id>', views.update_meal_option, name='update_meal_option'),
    path('mealsEdit/edit_meal_ingredients/<meal_id>', views.edit_meal_ingredients, name='edit_meal_ingredients'),
    path('mealsEdit/edit_meal_ingredients/<meal_id>/generate_shopping_list_for_meal',
         views.generate_shopping_list_for_meal, name='generate_shopping_list_for_meal'),
    path('mealsEdit/add_ingredient/<meal_id>', views.add_ingredient, name='add_ingredient'),
    path('mealsEdit/add_recipe/<meal_id>', views.add_recipe, name='add_recipe'),
    path('mealsEdit/update_ingredient/<meal_id>/<ingredient_id>', views.update_ingredient, name='update_ingredient'),
    path('mealsEdit/delete_ingredient/<meal_id>/<ingredient_id>', views.delete_ingredient, name='delete_ingredient'),
]
