from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.views.decorators.http import require_POST

from meals.forms import MealForm, IngredientForm, MealOptionForm
from meals.models import MealOption, Meal, Ingredient


@login_required(login_url='/accounts/login')
def meals(request):
    meals_options = MealOption.objects.filter(user=request.user)
    meals_options_dict = {}
    for i in range(len(meals_options)):
        meals_in_meals_options = Meal.objects.filter(meal_option=meals_options[i])
        meals = []
        for meal in meals_in_meals_options:
            # meal_option_meals = {meals_options[i]: meal}
            meals.append(meal)

        meals_options_dict[meals_options[i]] = meals
    print(meals_options_dict)
    context = {
        'meals_options_dict': meals_options_dict,
    }
    return render(request, 'meals/meals_list.html', context)


def edit_meals(request):
    form = MealForm(request.POST)
    form_ingredient = IngredientForm(request.POST)
    form_meal_option = MealOptionForm(request.POST)
    meals_options = MealOption.objects.filter(user=request.user)
    meals_options_dict = {}
    for i in range(len(meals_options)):
        meals_in_meals_options = Meal.objects.filter(meal_option=meals_options[i])
        meals = []
        for meal in meals_in_meals_options:
            # meal_option_meals = {meals_options[i]: meal}
            meals.append(meal)

        meals_options_dict[meals_options[i]] = meals

    context = {
        'form': form,
        'meals_options_dict': meals_options_dict,
        'form_ingredient': form_ingredient,
        'form_meal_option': form_meal_option
    }
    return render(request, 'meals/edit.html', context)


@require_POST
def add_meal(request, meal_option_id):
    form = MealForm(request.POST)
    meal_option = get_object_or_404(MealOption, pk=meal_option_id)
    meal = get_object_or_404(Meal, pk=meal_option_id)
    if form.is_valid():
        new_meal = Meal(name=request.POST['name'], user=request.user, meal_option=meal_option)
        new_meal.save()

        ingredients = request.POST['ingredients']
        ingredients_list = ingredients.splitlines()
        # print(ingredients_list)
        for item in ingredients_list:
            ingredient_properties_list = item.split(' - ')
            ingredient = ingredient_properties_list[0]
            quantity = ingredient_properties_list[1]
            shop = ingredient_properties_list[2]

            # print(ingredient_properties_list)
            new_ingredient = Ingredient(user=request.user, meal_id=new_meal, name=ingredient, quantity=quantity,
                                        shop=shop)
            new_ingredient.save()
    return redirect('meals:edit_meals')

@require_POST
def add_meal_option(request):
    form_meal_option = MealOptionForm(request.POST)

    new_meal_option = MealOption(user_id=request.user.id, meal_option=request.POST['meal_option'])
    print("sadfadf",new_meal_option)
    new_meal_option.save()

    return redirect('meals:edit_meals')