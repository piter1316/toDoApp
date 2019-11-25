import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.views.decorators.http import require_POST

from meals.forms import MealForm, IngredientForm, MealOptionForm
from meals.models import MealOption, Meal, Ingredient, MealsList


@login_required(login_url='/accounts/login')
def meals(request):
    meals_options = MealOption.objects.filter(user=request.user)
    meals_options_dict = {}

    for i in range(len(meals_options)):
        meals_in_meals_options = Meal.objects.filter(meal_option=meals_options[i])
        meals_list = []
        for meal in meals_in_meals_options:
            meals_list.append(meal)
        meals_options_dict[meals_options[i]] = meals_list

    user_meals_options = MealOption.objects.filter(user=request.user).order_by('position')
    meals_list = MealsList.objects.all().filter(user=request.user)
    days = []

    day_meal_option_meal_list = []
    for item in meals_list:
        while item.day not in days:
            days.append(item.day)

    for day in days:
        meals_on_day = MealsList.objects.all().filter(user=request.user, day=day).order_by('meal_option__position')
        day_meals_list = []
        for meal in meals_on_day:
            day_meals_list.append(meal.meal.name)
        day_meal_option_meal_list.append({day: day_meals_list})
    context = {
        'meals_options_dict': meals_options_dict,
        'meals_list': meals_list,
        'user_meals_options': user_meals_options,
        'day_meal_option_meal_list': day_meal_option_meal_list
    }
    return render(request, 'meals/meals_list.html', context)


def edit_meals(request):
    form = MealForm(request.POST)
    form_ingredient = IngredientForm(request.POST)
    form_meal_option = MealOptionForm(request.POST)
    meals_options = MealOption.objects.filter(user=request.user).order_by('position')
    meals_options_dict = {}
    for i in range(len(meals_options)):
        meals_in_meals_options = Meal.objects.filter(meal_option=meals_options[i])
        meals = []
        for meal in meals_in_meals_options:
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
        for item in ingredients_list:
            ingredient_properties_list = item.split(' - ')
            ingredient = ingredient_properties_list[0]
            quantity = ingredient_properties_list[1]
            shop = ingredient_properties_list[2]

            new_ingredient = Ingredient(user=request.user, meal_id=new_meal, name=ingredient, quantity=quantity,
                                        shop=shop)
            new_ingredient.save()
    return redirect('meals:edit_meals')


@require_POST
def add_meal_option(request):
    form_meal_option = MealOptionForm(request.POST)
    new_meal_option = MealOption(user_id=request.user.id, meal_option=request.POST['meal_option'])
    new_meal_option.save()
    return redirect('meals:edit_meals')


@require_POST
def generate_meals_list(request):
    user_meals_options = request.POST.getlist('mealsOptions[]')
    how_many_days = request.POST['howManyDays']
    twice_the_same_meal = request.POST['twiceTheSameMeal']
    print('ILOSć DNI', how_many_days)
    print('dwa razy', twice_the_same_meal)

    for option in user_meals_options:
        option_meals_list = []
        meals_in_option = Meal.objects.filter(meal_option=option, user=request.user)
        meal_option = MealOption.objects.filter(user=request.user, pk=option)
        for meal in meals_in_option:
            option_meals_list.append(meal)
            random_meals_list = []
        limit = 0
        for i in range(int(how_many_days)):
            random_meal = random.choice(option_meals_list)
            if random_meal not in random_meals_list:
                random_meals_list.append(random_meal)
            else:
                break

        print(meal_option, random_meals_list)
    return redirect('meals:index')
