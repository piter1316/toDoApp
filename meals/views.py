import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.views.decorators.http import require_POST

from meals.forms import MealForm, IngredientForm, MealOptionForm
from meals.models import MealOption, Meal, Ingredient, MealsList, Week


def days_generator(first, how_many):
    days = ['PN', 'WT', 'ŚR', 'CZW', 'PT', 'SB', 'ND']
    days_list = []
    for i in range(how_many):
        days_list.append(days[first])
        first += 1
        if first == len(days):
            first = 0
    return days_list


def get_maximum_no_of_days(request):
    user_meals_options = MealOption.objects.filter(user=request.user)
    no_of_meals_in_option = []
    for option in user_meals_options:
        meals_in_option = Meal.objects.filter(user=request.user, meal_option=option)
        no_of_meals_in_option.append(len(meals_in_option))
    return min(no_of_meals_in_option)


@login_required(login_url='/accounts/login')
def meals(request):
    in_meals_list =True
    meals_options = MealOption.objects.filter(user=request.user)
    meals_options_dict = {}

    for i in range(len(meals_options)):
        meals_in_meals_options = Meal.objects.filter(meal_option=meals_options[i])
        meals_list = []
        for meal in meals_in_meals_options:
            meals_list.append(meal)
        meals_options_dict[meals_options[i]] = meals_list

    user_meals_options = MealOption.objects.filter(user=request.user).order_by('position')
    generated_user_meals_options = MealsList.objects.filter(user=request.user).order_by('meal_option__position').values(
        'meal_option__meal_option').distinct()
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
            day_meals_list.append(meal)
        day_meal_option_meal_list.append({day: day_meals_list})

    maximum_no_of_days_to_generate = get_maximum_no_of_days(request)
    first_day_input_list = Week.objects.all()

    context = {
        'meals_options_dict': meals_options_dict,
        'meals_list': meals_list,
        'user_meals_options': user_meals_options,
        'generated_user_meals_options': generated_user_meals_options,
        'day_meal_option_meal_list': day_meal_option_meal_list,
        'maximum_no_of_days_to_generate': maximum_no_of_days_to_generate,
        'in_meals_list': in_meals_list,
        'first_day_input_list': first_day_input_list
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
        'form_meal_option': form_meal_option,
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
    twice_the_same_meal = request.POST.get('twice_the_same_meal', False)
    first_day = int(request.POST['first_day'])
    MealsList.objects.filter(user=request.user).delete()
    for option in user_meals_options:
        option_meals_list = []
        meals_in_option = Meal.objects.filter(meal_option=option, user=request.user)
        meal_option = get_object_or_404(MealOption, pk=option, user=request.user)
        for meal in meals_in_option:
            option_meals_list.append(meal)
        random_meals_list = []
        if twice_the_same_meal:
            if int(how_many_days) % 2 == 0:
                number_of_different_meals = int(int(how_many_days) / 2)
                for k in range(number_of_different_meals):
                    while len(random_meals_list) < int(how_many_days):
                        item = random.choice(option_meals_list)
                        random_meals_list.append(item)
                        random_meals_list.append(item)
                        option_meals_list.remove(item)
            else:
                number_of_different_meals = int((int(how_many_days) / 2)) + 1
                for j in range(number_of_different_meals):
                    while len(random_meals_list) < int(how_many_days):
                        item = random.choice(option_meals_list)
                        if len(random_meals_list) == int(how_many_days) - 1:
                            random_meals_list.append(item)
                            break
                        else:
                            random_meals_list.append(item)
                            random_meals_list.append(item)
                            option_meals_list.remove(item)
        else:
            for i in range(int(how_many_days)):
                while len(random_meals_list) < int(how_many_days):
                    item = random.choice(option_meals_list)
                    random_meals_list.append(item)
                    option_meals_list.remove(item)
        days = days_generator(first_day, int(how_many_days))
        for k in range(len(random_meals_list)):
            new_meals_list = MealsList(day=days[k], meal_id=random_meals_list[k].id, meal_option_id=meal_option.id,
                                       user_id=request.user.id)
            new_meals_list.save()
    return redirect('meals:index')
