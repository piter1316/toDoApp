import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.urls import reverse
from django.views.decorators.http import require_POST

from meals.forms import MealForm, IngredientForm, MealOptionForm
from meals.models import MealOption, Meal, Ingredient, MealsList, Week, Unit


def days_generator(first, how_many):
    days = ['PN', 'WT', 'ŚR', 'CZW', 'PT', 'SB', 'ND']
    days_list = []
    itr = ''
    space = ''
    for i in range(how_many):
        days_list.append(days[first] + space + str(itr))
        first += 1
        if first == len(days):
            first = 0
            if itr == '':
                itr = 1
            itr += 1
            space = '_'
    return days_list


def get_maximum_no_of_days(request):
    user_meals_options = MealOption.objects.filter(user=request.user)
    no_of_meals_in_option = []
    for option in user_meals_options:
        meals_in_option = Meal.objects.filter(user=request.user, meal_option=option, special=0)
        no_of_meals_in_option.append(len(meals_in_option))
    if len(no_of_meals_in_option) > 0:
        min_no_of_meals_in_option = min(no_of_meals_in_option)
        return min_no_of_meals_in_option
    else:
        return 0


@login_required(login_url='/accounts/login')
def meals(request):
    in_meals_list = True
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
            all_meals = Meal.objects.filter(user=request.user, meal_option_id=meal.meal_option.id)
            day_meals_list.append({meal: all_meals})
        day_meal_option_meal_list.append({day: day_meals_list})

    maximum_no_of_days_to_generate = get_maximum_no_of_days(request)
    first_day_input_list = Week.objects.all()
    user_meals_options_select = MealsList.objects.filter(user=request.user).order_by('meal_option__position').values(
        'meal_option_id', 'meal_option_id__meal_option').distinct()
    option_meals_dict = {}
    for option in user_meals_options_select:
        option_meals_list = []
        meals_in_option = Meal.objects.filter(meal_option=option['meal_option_id'], user=request.user)
        meal_option = get_object_or_404(MealOption, pk=option['meal_option_id'], user=request.user)
        for meal in meals_in_option:
            option_meals_list.append(meal)
        option_meals_dict[meal_option] = option_meals_list

    context = {
        'meals_options_dict': meals_options_dict,
        'meals_list': meals_list,
        'user_meals_options': user_meals_options,
        'generated_user_meals_options': generated_user_meals_options,
        'day_meal_option_meal_list': day_meal_option_meal_list,
        'maximum_no_of_days_to_generate': maximum_no_of_days_to_generate,
        'in_meals_list': in_meals_list,
        'first_day_input_list': first_day_input_list,
        'option_meals_dict': option_meals_dict
    }
    return render(request, 'meals/meals_list.html', context)


def edit_meals(request):
    form = MealForm(request.POST)
    form_ingredient = IngredientForm(request.POST)
    form_meal_option = MealOptionForm(request.POST)
    meals_options = MealOption.objects.filter(user=request.user).order_by('position')
    meals_options_dict = {}
    units = Unit.objects.all()
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
        'units': units,
    }
    return render(request, 'meals/edit.html', context)


@require_POST
def add_meal(request, meal_option_id):
    form = MealForm(request.POST)
    meal_option = get_object_or_404(MealOption, pk=meal_option_id)
    # meal = get_object_or_404(Meal, pk=meal_option_id)
    if 'special' in request.POST:
        special = request.POST['special']
        if special == 'on':
            special = True
    else:
        special = False
    if form.is_valid():
        new_meal = Meal(name=request.POST['name'], user=request.user, meal_option=meal_option, special=special)
        new_meal.save()
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
        meals_in_option = Meal.objects.filter(meal_option=option, user=request.user, special=0)
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
        print(days)
        print(len(random_meals_list))
        for k in range(len(random_meals_list)):
            new_meals_list = MealsList(day=days[k], meal_id=random_meals_list[k].id, meal_option_id=meal_option.id,
                                       user_id=request.user.id)
            new_meals_list.save()
    return redirect('meals:index')


@require_POST
def update_meals_list(request):
    print(request.POST)
    record_id = request.POST['record_id']
    to_update = request.POST['to_update']

    MealsList.objects.filter(pk=int(record_id)).update(meal_id=to_update)
    return redirect('meals:index')


def delete_meal_option(request, meal_option_id):
    MealOption.objects.filter(pk=meal_option_id).delete()
    return redirect('meals:edit_meals')


def edit_meal(request, meal_id):
    meal = Meal.objects.filter(user_id=request.user, pk=meal_id)
    ingredients = Ingredient.objects.filter(user=request.user, meal_id=meal_id)
    units = Unit.objects.all()
    if meal[0].recipe:
        recipe_rows = len(meal[0].recipe.split('\n'))
        print(recipe_rows)
    else:
        recipe_rows = 1

    context = {
        'meal': meal,
        'ingredients': ingredients,
        'units': units,
        'recipe_rows': recipe_rows
    }
    return render(request, 'meals/meal_edit.html', context)


def add_ingredient(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    ingredient = request.POST['ingredient'].lower()
    quantity = request.POST['quantity']
    unit = request.POST['unit']
    shop = request.POST['shop'].upper()

    new_ingredient = Ingredient(user=request.user, meal_id=meal, name=ingredient, quantity=quantity,
                                shop=shop, unit_id=unit)
    new_ingredient.save()
    return redirect('meals:edit_meal', meal_id=meal_id)


def add_recipe(request, meal_id):
    recipe = request.POST['update_recipe_textarea']
    Meal.objects.filter(pk=meal_id).update(recipe=recipe)
    return redirect('meals:edit_meal', meal_id=meal_id)


def update_ingredient(request, ingredient_id, meal_id):
    print(ingredient_id)
    new_ingredient_name = request.POST['new_ingredient_name']
    new_quantity = request.POST['new_quantity']
    new_unit = request.POST['new_unit']
    new_shop = request.POST['new_shop']

    Ingredient.objects.filter(pk=ingredient_id).update(name=new_ingredient_name, quantity=new_quantity, unit=new_unit,
                                                       shop=new_shop)
    return redirect('meals:edit_meal', meal_id=meal_id)


def delete_ingredient(request, meal_id, ingredient_id):
    Ingredient.objects.filter(pk=ingredient_id).delete()
    return redirect('meals:edit_meal', meal_id=meal_id)


def delete_meal(request, meal_id):
    Meal.objects.filter(pk=meal_id).delete()
    return redirect('meals:edit_meals')


def purge_meals_list(request):
    MealsList.objects.all().delete()
    return redirect('meals:index')


def update_meal_option(request, meal_option_id):
    new_name = request.POST['new_meal_option_name']
    MealOption.objects.filter(pk=meal_option_id).update(meal_option=new_name)
    return redirect('meals:edit_meals')