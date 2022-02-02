import random
import time
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.views.decorators.http import require_POST

from meals.forms import MealForm, IngredientForm, MealOptionForm
from meals.models import MealOption, Meal, Ingredient, MealsList, Week, Unit, MealIngredient, Shop, ProductDivision
from shopping.models import ShoppingList, Products


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


def appended_days_generator(request, first, how_many):
    days = ['PN', 'WT', 'ŚR', 'CZW', 'PT', 'SB', 'ND']
    days_list = []
    meals_list_ids = MealsList.objects.filter(user_id=request, current=1)
    itr = meals_list_ids.reverse()[0].id
    space = '_'
    for i in range(how_many):
        days_list.append(days[first] + space + str(itr))
        first += 1
        if first == len(days):
            first = 0
            if itr == '':
                itr = 1
            itr += 1
    return days_list


def get_maximum_no_of_days(request):
    user_meals_options = MealOption.objects.filter(user=request.user, is_taken_to_generation=1)
    no_of_meals_in_option = []
    for option in user_meals_options:
        meals_in_option = Meal.objects.filter(user=request.user, meal_option=option, special=0)
        no_of_meals_in_option.append(len(meals_in_option))
    if len(no_of_meals_in_option) > 0:
        min_no_of_meals_in_option = min(no_of_meals_in_option)
        return min_no_of_meals_in_option
    else:
        return 0


def get_maximum_no_of_days_no_repeat(request):
    current_meals_list = MealsList.objects.filter(user=request.user,current=1)
    current_meals = []
    no_of_meals_in_option = []
    for item in (list(current_meals_list)):
        if item.meal_id:
            current_meals.append(item.meal_id)
    user_meals_options = MealOption.objects.filter(user=request.user)
    for option in user_meals_options:
        meals_in_option = Meal.objects.filter(meal_option=option, user=request.user, special=0)
        option_meals_list = []
        for meal in meals_in_option:
            if meal.id not in current_meals:
                option_meals_list.append(meal)
        no_of_meals_in_option.append(len(option_meals_list))
    if len(no_of_meals_in_option) > 0:
        min_no_of_meals_in_option = min(no_of_meals_in_option)
        return min_no_of_meals_in_option
    else:
        return 0


@login_required(login_url='/accounts/login')
def meals(request, current=1):
    in_meals_list = True
    user_meals_options = MealOption.objects.filter(user=request.user, is_taken_to_generation=1).order_by('position')
    generated_user_meals_options = MealsList.objects.filter(user=request.user, current=current).order_by('meal_option__position').values(
        'meal_option__meal_option', 'meal_option_id').distinct()
    all_user_meals_options = MealOption.objects.filter(user=request.user).order_by('position').values('meal_option', 'id')
    meals_list = MealsList.objects.all().filter(user=request.user, current=current)
    days = []
    all_meals_in_option_dict = {}
    all_meals = []
    for option in all_user_meals_options:
        meals_in_option = Meal.objects.filter(meal_option_id=option['id'], user=request.user).order_by(
            'name')
        calories = 0
        all_meals_in_option = []
        for meal in meals_in_option:
            all_meals.append(meal.id)
            calories_sum = 0
            all_meals_in_option.append([meal, calories_sum])
        all_meals_in_option_dict[option['id']] = all_meals_in_option
    sql = """
    SELECT
        *
    FROM
        `meals_mealingredient`
    INNER JOIN `meals_ingredient` ON (
        `meals_mealingredient`.`ingredient_id_id` = `meals_ingredient`.`id`
    )
    WHERE
        `meal_id_id` IN {}
        """.format(str(all_meals).replace('[','(').replace(']',')'))
    all_ingredients = MealIngredient.objects.raw(sql)

    meal_ingredients_dict = {}
    for meal in all_meals:
        ingredients_for_meal = []
        for ingredient in all_ingredients:
            if meal == ingredient.meal_id_id:
                ingredients_for_meal.append(ingredient)

        meal_ingredients_dict[meal] = ingredients_for_meal
    for meal, ingredients in meal_ingredients_dict.items():
        kcal = []
        short_expiry = []

        for ingredient in ingredients:
            if ingredient.short_expiry:
                short_expiry.append(1)

            kcal.append((ingredient.calories_per_100_gram * ingredient.quantity/100))
        for option, meals_in_option in all_meals_in_option_dict.items():
            for m in meals_in_option:
                if m[0].id == meal:
                    m[1] = [round(sum(kcal)), short_expiry]
    day_meal_option_meal_list = []
    # table
    for item in meals_list:
        while item.day not in days:
            days.append(item.day)
    day_calories = []
    meals_on_day = MealsList.objects.select_related('meal').filter(user=request.user, current=current, day__in=days).order_by('meal_option__position')
    for day in days:
        # meals_on_day = MealsList.objects.select_related('meal').filter(user=request.user, current=current, day=day).order_by(
        #     'meal_option__position')

        day_meals_list = []
        meals = []
        meal_ingredients = []
        meal_protein = []
        meal_fat = []
        meal_carbohydrates = []

        for meal in meals_on_day:
            if day == meal.day:
                all_meals_to_select = []
                calories = 0
                protein = 0
                fat = 0
                carbohydrates = 0
                ingredients_list = []
                tmp_extra = []
                if meal.meal_id:
                    ingredients_list = meal_ingredients_dict[meal.meal_id]
                    if meal.extras:
                        ingredients_list.extend(meal_ingredients_dict[meal.extras.id])
                        tmp_extra = meal_ingredients_dict[meal.extras.id]
                else:
                    if meal.extras:
                        ingredients_list.extend(meal_ingredients_dict[meal.extras.id])
                        tmp_extra = meal_ingredients_dict[meal.extras.id]
                    else:
                        calories = 0

                for ingr in ingredients_list:
                    calories += (ingr.quantity / 100) * int(ingr.calories_per_100_gram)
                    protein += (ingr.quantity / 100) * int(ingr.protein_per_100_gram)
                    fat += (ingr.quantity / 100) * int(ingr.fat_per_100_gram)
                    carbohydrates += (ingr.quantity / 100) * int(ingr.carbohydrates_per_100_gram)
                    meal_ingredients.append(round(calories, 0))
                    meal_protein.append(round(protein, 0))
                    meal_fat.append(round(fat, 0))
                    meal_carbohydrates.append(round(carbohydrates, 0))
                    calories = 0
                    protein = 0
                    fat = 0
                    carbohydrates = 0
                meals.append(meal.meal_id)
                day_meals_list.append({meal: all_meals_in_option_dict.get(meal.meal_option_id)})
                for item in tmp_extra:
                    if item in ingredients_list:
                        ingredients_list.remove(item)
                print(ingredients_list)
        day_calories.append({day: [round(sum(meal_ingredients), 0)]})
        day_meal_option_meal_list.append(
            [{day: day_meals_list},
             [round(sum(meal_ingredients)), round(sum(meal_protein)), round(sum(meal_fat)),
              round(sum(meal_carbohydrates))]])
    maximum_no_of_days_to_generate = get_maximum_no_of_days(request)
    maximum_no_of_days_to_generate_no_repeat = get_maximum_no_of_days_no_repeat(request)
    first_day_input_list = Week.objects.all()
    user_meals_options_select = MealsList.objects.filter(user=request.user, current=current).order_by('meal_option__position').values(
        'meal_option_id', 'meal_option_id__meal_option').distinct()
    option_meals_dict = {}
    user_meals_options_select = []
    for option in user_meals_options_select:
        option_meals_list = []
        meals_in_option = Meal.objects.filter(meal_option=option['meal_option_id'], user=request.user)
        meal_option = option
        for meal in meals_in_option:
            option_meals_list.append(meal)
        option_meals_dict[meal_option] = option_meals_list
    # average calories for whole mealsList
    all_meals = meals_list
    meal_options = generated_user_meals_options
    meals = MealsList.objects.select_related('meal').filter(user=request.user, current=current)
    ingredients_total = []
    tmp_extra_total = []
    calories_total = 0
    protein_total = 0
    fat_total = 0
    carb_total = 0
    calories = 0
    protein = 0
    fat = 0
    carb = 0
    # for key, value in meal_ingredients_dict.items():
    #     print(key, value)
    for meal in meals:
        print(meal.id)
        if meal.meal_id:
            ingredients_total = meal_ingredients_dict[meal.meal_id]
            if meal.extras:
                ingredients_total.extend(meal_ingredients_dict[meal.extras.id])
                tmp_extra_total = meal_ingredients_dict[meal.extras.id]
        else:
            ingredients_total = []
            if meal.extras:
                ingredients_total.extend(meal_ingredients_dict[meal.extras.id])
                tmp_extra_total = meal_ingredients_dict[meal.extras.id]

        for ingr in ingredients_total:
            calories += (ingr.quantity / 100) * int(ingr.calories_per_100_gram)
            protein += (ingr.quantity / 100) * int(ingr.protein_per_100_gram)
            fat += (ingr.quantity / 100) * int(ingr.fat_per_100_gram)
            carb += (ingr.quantity / 100) * int(ingr.carbohydrates_per_100_gram)
            calories_total += calories
            protein_total += protein
            fat_total += fat
            carb_total += carb
            calories = 0
            protein = 0
            fat = 0
            carb = 0
        for item in tmp_extra_total:
            if item in ingredients_total:
                ingredients_total.remove(item)

    try:
        meals_list_length = int(len(all_meals) / len(meal_options))
        average_clories_per_day = int(calories_total / meals_list_length)
        average_protein_per_day = int(protein_total / meals_list_length)
        average_fat_per_day = int(fat_total / meals_list_length)
        average_carb_per_day = int(carb_total / meals_list_length)
    except ZeroDivisionError:
        meals_list_length = 0
        average_clories_per_day = 0
        average_protein_per_day = 0
        average_carb_per_day = 0
        average_fat_per_day = 0
    context = {
        'meals_list': meals_list,
        'user_meals_options': user_meals_options,
        'generated_user_meals_options': generated_user_meals_options,
        'day_meal_option_meal_list': day_meal_option_meal_list, # dictionary to build table in template
        'maximum_no_of_days_to_generate': maximum_no_of_days_to_generate,
        'maximum_no_of_days_to_generate_default': maximum_no_of_days_to_generate * 2,
        'in_meals_list': in_meals_list,
        'first_day_input_list': first_day_input_list,
        'maximum_no_of_days_to_generate_no_repeat': maximum_no_of_days_to_generate_no_repeat,
        'average_clories_per_day': average_clories_per_day,
        'average_protein_per_day': average_protein_per_day,
        'average_fat_per_day': average_fat_per_day,
        'average_carb_per_day': average_carb_per_day,
        'current': int(current),
    }
    return render(request, 'meals/meals_list.html', context)


@login_required(login_url='/accounts/login')
def edit_meals(request):
    form = MealForm(request.POST)
    form_ingredient = IngredientForm(request.POST)
    form_meal_option = MealOptionForm(request.POST)
    meals_options = MealOption.objects.filter(user=request.user).order_by('position')
    meals_options_dict = {}
    units = Unit.objects.all()
    for i in range(len(meals_options)):
        meals = []
        meals_in_meals_options = MealIngredient.objects.select_related('meal_id').select_related('ingredient_id').filter(meal_id__meal_option=meals_options[i]).order_by('meal_id__name')
        meals_tmp = Meal.objects.filter(meal_option=meals_options[i]).order_by('name')
        for meal_tmp in meals_tmp:
            ingredients = []
            for meal in meals_in_meals_options:
                if meal_tmp == meal.meal_id:
                    ingredients.append(meal)
            calories = 0
            protein = 0
            fat = 0
            carbohydrates = 0
            for ingr in ingredients:
                calories += (ingr.quantity) / 100 * int(ingr.ingredient_id.calories_per_100_gram)
                protein += (ingr.quantity / 100) * int(ingr.ingredient_id.protein_per_100_gram)
                fat += (ingr.quantity / 100) * int(ingr.ingredient_id.fat_per_100_gram)
                carbohydrates += (ingr.quantity / 100) * int(ingr.ingredient_id.carbohydrates_per_100_gram)
            meals.append([meal_tmp, [round(calories), round(protein), round(fat), round(carbohydrates)]])
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
        new_meal = Meal(name=request.POST['name'].lower(), user=request.user, meal_option=meal_option,
                        special=special)
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
    empty_meals_list = request.POST.get('empty_meals_list', False)
    first_day = int(request.POST['first_day']) - 1
    append_existing = request.POST.get('append_existing', False)
    no_repetition = request.POST.get('no_repetition', False)
    current_meals_list = MealsList.objects.filter(user=request.user, current=1)
    previous_meals_list = MealsList.objects.filter(user=request.user, current=0)
    current_meals = []
    for item in (list(current_meals_list)):
        if item.meal_id:
            current_meals.append(item.meal_id)
    if append_existing:
        days = appended_days_generator(request.user, first_day, int(how_many_days))
        current_days = int(len(current_meals_list)/len(user_meals_options))

    else:
        previous_meals_list.delete()
        current_meals_list.update(current=0)
        days = days_generator(first_day, int(how_many_days))
        current_days = 0
    for option in user_meals_options:
        option_meals_list = []
        meals_in_option = Meal.objects.filter(meal_option=option, user=request.user, special=0)
        ingredients_with_short = MealIngredient.objects.select_related('meal_id').select_related('ingredient_id').filter(ingredient_id__short_expiry=1, meal_id__meal_option_id=option)
        meals_with_short_expiry_in_option = []
        meals_without_short_expiry_in_option = []
        for ingredient in ingredients_with_short:
            meals_with_short_expiry_in_option.append(ingredient.meal_id.id)
        meal_option = get_object_or_404(MealOption, pk=option, user=request.user)
        for meal in meals_in_option:
            if meal.id not in current_meals:
                option_meals_list.append(meal)

        for item in option_meals_list:
            if item.pk not in meals_with_short_expiry_in_option:
                meals_without_short_expiry_in_option.append(item)
        random_meals_list = []
        if twice_the_same_meal:
            day = 1
            if append_existing:
                day = current_days + 1
            if int(how_many_days) % 2 == 0:
                while len(random_meals_list) < int(how_many_days):
                    if day > 4:
                        item = random.choice(meals_without_short_expiry_in_option)
                        random_meals_list.append(item)
                        random_meals_list.append(item)
                        meals_without_short_expiry_in_option.remove(item)
                        day += 2
                    else:
                        item = random.choice(option_meals_list)
                        random_meals_list.append(item)
                        random_meals_list.append(item)
                        option_meals_list.remove(item)
                        if item in meals_without_short_expiry_in_option:
                            meals_without_short_expiry_in_option.remove(item)

                        day += 2
            else:
                day = 1
                if append_existing:
                    day = current_days + 1
                while len(random_meals_list) < int(how_many_days):
                    if day > 4:
                        item = random.choice(meals_without_short_expiry_in_option)
                        if len(random_meals_list) == int(how_many_days) - 1:
                            random_meals_list.append(item)
                            break
                        else:
                            random_meals_list.append(item)
                            random_meals_list.append(item)
                            meals_without_short_expiry_in_option.remove(item)
                            option_meals_list.remove(item)
                            day += 2
                    else:
                        item = random.choice(option_meals_list)
                        if len(random_meals_list) == int(how_many_days) - 1:
                            random_meals_list.append(item)
                            break
                        else:
                            random_meals_list.append(item)
                            random_meals_list.append(item)
                            option_meals_list.remove(item)
                            if item in meals_without_short_expiry_in_option:
                                meals_without_short_expiry_in_option.remove(item)
                            day += 2
        else:
            for i in range(int(how_many_days)):
                day = 1
                if append_existing:
                    day = current_days + 1
                while len(random_meals_list) < int(how_many_days):
                    if day > 4:
                        item = random.choice(meals_without_short_expiry_in_option)
                        random_meals_list.append(item)
                        meals_without_short_expiry_in_option.remove(item)
                        day += 1
                    else:
                        item = random.choice(option_meals_list)
                        random_meals_list.append(item)
                        option_meals_list.remove(item)
                        if item in meals_without_short_expiry_in_option:
                            meals_without_short_expiry_in_option.remove(item)
                        day += 1
        new_meals_list_list = []
        if empty_meals_list:

            for k in range(len(random_meals_list)):
                new_meals_list = MealsList(day=days[k], meal_id=None, meal_option_id=meal_option.id,
                                           user_id=request.user.id, current=1)
                new_meals_list_list.append(new_meals_list)
            MealsList.objects.bulk_create(new_meals_list_list)
        else:
            new_meals_list_list = []
            for k in range(len(random_meals_list)):
                new_meals_list = MealsList(day=days[k], meal_id=random_meals_list[k].id, meal_option_id=meal_option.id,
                                           user_id=request.user.id, current=1)
                new_meals_list_list.append(new_meals_list)
            MealsList.objects.bulk_create(new_meals_list_list)
    return redirect('/mealsList/1')


@require_POST
def update_meals_list(request):
    record_id = request.POST['record_id']
    to_update = request.POST['to_update']

    MealsList.objects.filter(pk=int(record_id)).update(meal_id=to_update)
    return redirect('/mealsList/1')


def delete_meal_option(request, meal_option_id):
    MealOption.objects.filter(pk=meal_option_id).delete()
    return redirect('meals:edit_meals')

@login_required(login_url='/accounts/login')
def edit_meal_ingredients(request, meal_id):
    meal = Meal.objects.filter(user_id=request.user, pk=meal_id)
    ingredients = MealIngredient.objects.select_related('ingredient_id').filter(meal_id=meal_id)
    user_ingredients = Ingredient.objects.filter(user=request.user).order_by('name')
    user_shops = Shop.objects.filter(user=request.user)
    units = Unit.objects.all()
    if meal[0].recipe:
        recipe_rows = len(meal[0].recipe.split('\n'))
    else:
        recipe_rows = 1
    calories = 0
    protein = 0
    fat = 0
    carbohydrates = 0
    for ingr in ingredients:
        calories += (ingr.quantity) / 100 * int(ingr.ingredient_id.calories_per_100_gram)
        protein += (ingr.quantity) / 100 * int(ingr.ingredient_id.protein_per_100_gram)
        fat += (ingr.quantity) / 100 * int(ingr.ingredient_id.fat_per_100_gram)
        carbohydrates += (ingr.quantity) / 100 * int(ingr.ingredient_id.carbohydrates_per_100_gram)
    context = {
        'meal': meal,
        'ingredients': ingredients,
        'units': units,
        'recipe_rows': recipe_rows,
        'user_ingredients': user_ingredients,
        'user_shops': user_shops,
        'calories': round(calories),
        'protein': round(protein),
        'fat': round(fat),
        'carbohydrates': round(carbohydrates)
    }
    return render(request, 'meals/meal_edit.html', context)

@login_required(login_url='/accounts/login')
def add_ingredient(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    ingredient = request.POST['ingredient']
    quantity = request.POST['quantity']
    unit = request.POST['unit']
    ingredient_instance = get_object_or_404(Ingredient, pk=ingredient)
    quantity_per_unit = ingredient_instance.weight_per_unit

    if unit != '2':
        quantity = float(quantity) * int(quantity_per_unit)

    new_ingredient = MealIngredient(meal_id=meal, ingredient_id=ingredient_instance, quantity=quantity)
    new_ingredient.save()
    return redirect('meals:edit_meal_ingredients', meal_id=meal_id)

@login_required(login_url='/accounts/login')
def add_recipe(request, meal_id):
    recipe = request.POST['update_recipe_textarea']
    Meal.objects.filter(pk=meal_id).update(recipe=recipe)
    return redirect('meals:edit_meal_ingredients', meal_id=meal_id)

@login_required(login_url='/accounts/login')
def update_ingredient(request, ingredient_id, meal_id):
    new_quantity = request.POST['new_quantity']
    new_unit = request.POST['new_unit']
    MealIngredient_instance = get_object_or_404(MealIngredient, pk=ingredient_id)
    ingredient_instance = get_object_or_404(Ingredient, pk=MealIngredient_instance.ingredient_id_id)
    quantity_per_unit = ingredient_instance.weight_per_unit
    if new_unit != '2':
        new_quantity = float(new_quantity) * int(quantity_per_unit)

    MealIngredient.objects.filter(pk=ingredient_id).update(quantity=new_quantity)
    return redirect('meals:edit_meal_ingredients', meal_id=meal_id)


def delete_ingredient(request, meal_id, ingredient_id):
    MealIngredient.objects.filter(pk=ingredient_id).delete()
    return redirect('meals:edit_meal_ingredients', meal_id=meal_id)


def delete_meal(request, meal_id):
    Meal.objects.filter(pk=meal_id).delete()
    return redirect('meals:edit_meals')


def purge_meals_list(request):
    MealsList.objects.filter(user=request.user, current=1).delete()
    return redirect('/mealsList/1')


def update_meal_option(request, meal_option_id):
    new_name = request.POST['new_meal_option_name']
    is_taken_to_generation = request.POST.get('is_taken_to_generation', 0)
    if is_taken_to_generation:
        is_taken_to_generation = 1
    MealOption.objects.filter(pk=meal_option_id).update(meal_option=new_name,
                                                        is_taken_to_generation=is_taken_to_generation)
    return redirect('meals:edit_meals')


def update_meal_name(request, meal_id):
    new_meal_name = request.POST['new_meal_name']
    edit_special = request.POST.get('edit_special', False)
    if edit_special == 'true':
        edit_special = True
    else:
        edit_special = False
    Meal.objects.filter(pk=meal_id).update(name=new_meal_name, special=edit_special)
    return redirect('meals:edit_meal_ingredients', meal_id=meal_id)


def generate_shopping_lists(request):
    meals = MealsList.objects.select_related('meal', 'extras').filter(user=request.user, current=1)
    shops = Shop.objects.filter(user_id=request.user)
    shops = list(shops)
    shops.append(None)
    ingredients_list = []
    ingr_qt_dict = {}
    shopping_lists = []
    how_many_people = request.POST['how_many_people']
    delete_generated_shopping_lists = request.POST.get('delete_generated_shopping_lists', False)
    if delete_generated_shopping_lists:
        ShoppingList.objects.filter(user_id=request.user, generated=1).delete()
    if how_many_people == '':
        how_many_people = 1
    else:
        how_many_people = int(how_many_people)
    for meal in meals:
        if meal.extras:
            meal_instance = meal.extras.id
            for ingredient in MealIngredient.objects.select_related('ingredient_id').filter(meal_id=meal_instance):
                ingredients_list.append(ingredient)
        if meal.meal_id:
            meal_instance = meal.meal_id
            for ingredient in MealIngredient.objects.select_related('ingredient_id').filter(meal_id=meal_instance):
                ingredients_list.append(ingredient)
    for shop in shops:
        for ingredient in ingredients_list:
            ingredient_object = ingredient.ingredient_id
            shop_id = ingredient.ingredient_id.shop_id
            try:
                id = shop.id
            except Exception:
                id = None
            if id == shop_id:
                if ingredient_object in ingr_qt_dict.keys():
                    qt = ingr_qt_dict[ingredient_object][0]
                    qt += ingredient.quantity
                    ingr_qt_dict[ingredient_object] = [qt, ingredient_object.weight_per_unit ]
                else:
                    ingr_qt_dict[ingredient_object] = [ingredient.quantity, ingredient_object.weight_per_unit]

        for ingr, qt in ingr_qt_dict.items():
            wpu = ingr.weight_per_unit
            if wpu == 0:
                wpu = 1
            ingr_qt_dict[ingr][0] = round((qt[0] / int(wpu)) * how_many_people, 2)
        if len(ingr_qt_dict) > 0:
            shopping_lists.append({shop: ingr_qt_dict})
        ingr_qt_dict = {}
    for item in shopping_lists:
        shop = list(item.keys())[0]
        if shop is None:
            shop = 'NIEPRZYPISANY'
        new_shopping_list = ShoppingList(user_id=request.user, name=shop, generated=1)
        new_shopping_list.save()
        for shop, shoping_list_items in item.items():
            new_list_position_list = []
            for shopping_item, qt in shoping_list_items.items():
                if qt[1] != 0:
                    unit = 1
                else:
                    unit = 2
                new_list_position = Products(product_name=shopping_item, quantity=qt[0],
                                             shopping_list_id_id=new_shopping_list.id,
                                             unit_id=unit, division_id = shopping_item.division)
                new_list_position_list.append(new_list_position)
            Products.objects.bulk_create(new_list_position_list)
    return redirect('shopping:shopping_list_index')


def delete_selected_days(request):
    meals_list_positions_to_delete_list = request.POST.getlist('mealsListPosition')
    for item in meals_list_positions_to_delete_list:
        MealsList.objects.filter(user=request.user, pk=item).delete()
    return redirect('/mealsList/1')


def edit_ingredients(request):
    user_ingredients = Ingredient.objects.filter(user=request.user).order_by('name')
    user_shops = Shop.objects.filter(user=request.user.id)
    user_divisions = ProductDivision.objects.filter(user=request.user).order_by('-priority')
    form = IngredientForm()
    context = {
        'user_ingredients': user_ingredients,
        'user_shops': user_shops,
        'form': form,
        'active_tab': 'shop',
        'user_divisions': user_divisions,
    }
    return render(request, 'meals/ingredients_edit.html', context)


def add_shop(request):
    new_shop_name = request.POST['new_shop_name']
    new_shop_name = new_shop_name.upper()
    new_shop = Shop(name=new_shop_name, user=request.user)
    new_shop.save()
    return redirect('/ingredientsEdit#shops')


def edit_shop(request):
    new_name = request.POST['new_name']
    shop_id = request.POST['shop_id']
    shop_to_edit = get_object_or_404(Shop, pk=int(shop_id))
    shop_to_edit.name = new_name.upper().strip()
    shop_to_edit.save()

    return redirect('/ingredientsEdit#shops')


def delete_shop(request, shop_id):
    Shop.objects.filter(pk=shop_id).delete()
    return redirect('/ingredientsEdit#shops')


def new_ingredient(request):
    new_ingredient_name = request.POST['ingr_name']
    kcal = request.POST.get('kcal', False)
    prot = request.POST.get('prot', False)
    fat = request.POST.get('fat', False)
    carb = request.POST.get('carb', False)
    avg_unit = request.POST.get('avg_unit', False)
    shop_select = request.POST.get('shop', False)
    short_expiry = request.POST.get('short_expiry', False)
    division = request.POST.get('division',1)
    if short_expiry:
        short_expiry = True

    if not kcal:
        kcal = 0
    if not prot:
        prot = 0
    if not fat:
        fat = 0
    if not carb:
        carb = 0
    if not avg_unit:
        avg_unit = 0
    if shop_select == 'None':
        shop = None
    else:
        shop = Shop.objects.get(pk=shop_select)
    new_ingredient = Ingredient(user=request.user, name=new_ingredient_name, calories_per_100_gram=kcal,
                                protein_per_100_gram=prot,
                                fat_per_100_gram=fat,
                                carbohydrates_per_100_gram=carb,
                                weight_per_unit=avg_unit, shop=shop, short_expiry=short_expiry, division_id=division)
    new_ingredient.save()
    return redirect('meals:edit_ingredients')


def delete_ingr(request, ingr_id):
    Ingredient.objects.filter(pk=ingr_id, user_id=request.user).delete()
    return redirect('meals:edit_ingredients')


def edit_ingredient(request, ingr_id):
    new_ingredient_name = request.POST['ingr_name']
    kcal = request.POST.get('kcal', False)
    prot = request.POST.get('prot', False)
    fat = request.POST.get('fat', False)
    carb = request.POST.get('carb', False)
    avg_unit = request.POST.get('avg_unit', False)
    shop_select = request.POST.get('shop', False)
    short_expiry = request.POST.get('short_expiry', False)
    division = request.POST.get('division', 1)
    if short_expiry:
        short_expiry = True

    if not kcal:
        kcal = 0
    if not prot:
        prot = 0
    if not fat:
        fat = 0
    if not carb:
        carb = 0
    if not avg_unit:
        avg_unit = 0
    if shop_select == 'None':
        shop = None
    else:
        shop = Shop.objects.get(pk=shop_select)
    if division == 1:
        division = ProductDivision.objects.get(pk=1)
    else:
        division = ProductDivision.objects.get(pk=division)


    edited_ingredient = Ingredient.objects.get(pk=ingr_id)
    edited_ingredient.name = new_ingredient_name
    edited_ingredient.calories_per_100_gram = kcal
    edited_ingredient.protein_per_100_gram = prot
    edited_ingredient.fat_per_100_gram = fat
    edited_ingredient.carbohydrates_per_100_gram = carb
    edited_ingredient.weight_per_unit = avg_unit
    edited_ingredient.shop = shop
    edited_ingredient.short_expiry = short_expiry
    edited_ingredient.division = division
    edited_ingredient.save()

    return redirect('meals:edit_ingredients')


def edit_division(request, division_id):
    division_to_edit = get_object_or_404(ProductDivision, pk=division_id, user=request.user)
    division_to_edit.division_name = request.POST['new_name']
    division_to_edit.save()
    return HttpResponse(str(division_id))


def edit_division_priority(request, division_id):
    division_to_edit = get_object_or_404(ProductDivision, pk=division_id, user=request.user)
    division_to_edit.priority = request.POST['new_priority']
    division_to_edit.save()
    return HttpResponse(str(division_id))


def add_new_division(request):
    if request.method == 'POST':
        print(request.POST)
        new_division = ProductDivision(division_name=request.POST['division_name'], priority=request.POST['division_priority'], user_id=request.user.id)
        new_division.save()
    return redirect('/ingredientsEdit#division')


def delete_division(request, division_id):
    try:
        ProductDivision.objects.filter(pk=division_id, user_id=request.user.id).delete()
    except Exception as e:
        messages.error(request, 'Podany dział zawiera produkty i nie zostanie usuniety.')
    return redirect('/ingredientsEdit#division')
