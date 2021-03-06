import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.views.decorators.http import require_POST

from meals.forms import MealForm, IngredientForm, MealOptionForm
from meals.models import MealOption, Meal, Ingredient, MealsList, Week, Unit, MealIngredient, Shop
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
    meals_list_ids = MealsList.objects.filter(user_id=request)
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


def get_maximum_no_of_days_no_repeat(request):
    current_meals_list = MealsList.objects.filter(user=request.user)
    current_meals = []
    no_of_meals_in_option = []
    for item in (list(current_meals_list)):
        if item.meal_id:
            meal = get_object_or_404(Meal, pk=item.meal_id)
            current_meals.append(meal)
    user_meals_options = MealOption.objects.filter(user=request.user)

    for option in user_meals_options:
        meals_in_option = Meal.objects.filter(meal_option=option, user=request.user, special=0)
        # meal_option = get_object_or_404(MealOption, pk=option, user=request.user)
        option_meals_list = []
        for meal in meals_in_option:
            if meal not in current_meals:
                option_meals_list.append(meal)
        no_of_meals_in_option.append(len(option_meals_list))
    if len(no_of_meals_in_option) > 0:
        min_no_of_meals_in_option = min(no_of_meals_in_option)
        return min_no_of_meals_in_option
    else:
        return 0


@login_required(login_url='/accounts/login')
def meals(request):
    in_meals_list = True
    user_meals_options = MealOption.objects.filter(user=request.user).order_by('position')
    generated_user_meals_options = MealsList.objects.filter(user=request.user).order_by('meal_option__position').values(
        'meal_option__meal_option', 'meal_option_id').distinct()
    meals_list = MealsList.objects.all().filter(user=request.user)
    days = []
    all_meals_in_option_dict = {}
    for option in generated_user_meals_options:
        meals_in_option = Meal.objects.filter(meal_option_id=option['meal_option_id'], user=request.user).order_by(
            'name')
        calories = 0
        all_meals_in_option = []
        for meal in meals_in_option:
            ingredients = MealIngredient.objects.select_related('ingredient_id').filter(meal_id=meal)
            meal_ingr = []

            for ingr in ingredients:
                ingr_obj = get_object_or_404(Ingredient, pk=ingr.ingredient_id.id)
                calories += (ingr.quantity / 100) * int(ingr_obj.calories_per_100_gram)
                meal_ingr.append(round(calories, 0))
                calories = 0
            all_meals_in_option.append([meal, sum(meal_ingr)])
        all_meals_in_option_dict[option['meal_option_id']] = all_meals_in_option

    day_meal_option_meal_list = []
    for item in meals_list:
        while item.day not in days:
            days.append(item.day)

    day_calories = []
    for day in days:
        meals_on_day = MealsList.objects.select_related('meal').filter(user=request.user, day=day).order_by(
            'meal_option__position')
        day_meals_list = []
        meals = []
        meal_ingredients = []
        meal_protein = []
        meal_fat = []
        meal_carbohydrates = []
        for meal in meals_on_day:
            try:
                one_meal = Meal.objects.get(id=meal.meal_id)
            except Exception:
                one_meal = None

            all_meals_to_select = []

            calories = 0
            protein = 0
            fat = 0
            carbohydrates = 0
            if one_meal:
                ingredients = MealIngredient.objects.select_related('ingredient_id').filter(meal_id=one_meal.id)

                for ingr in ingredients:
                    ingr_obj = get_object_or_404(Ingredient, pk=ingr.ingredient_id.id)
                    calories += (ingr.quantity / 100) * int(ingr_obj.calories_per_100_gram)
                    protein += (ingr.quantity / 100) * int(ingr_obj.protein_per_100_gram)
                    fat += (ingr.quantity / 100) * int(ingr_obj.fat_per_100_gram)
                    carbohydrates += (ingr.quantity / 100) * int(ingr_obj.carbohydrates_per_100_gram)
                    meal_ingredients.append(round(calories, 0))
                    meal_protein.append(round(protein, 0))
                    meal_fat.append(round(fat, 0))
                    meal_carbohydrates.append(round(carbohydrates, 0))
                    calories = 0
                    protein = 0
                    fat = 0
                    carbohydrates = 0
            else:
                calories = 0
            meals.append(one_meal)
            day_meals_list.append({meal: all_meals_in_option_dict.get(meal.meal_option.id)})
        day_calories.append({day: [round(sum(meal_ingredients), 0)]})
        day_meal_option_meal_list.append(
            [{day: day_meals_list},
             [round(sum(meal_ingredients)), round(sum(meal_protein)), round(sum(meal_fat)),
              round(sum(meal_carbohydrates))]])

    maximum_no_of_days_to_generate = get_maximum_no_of_days(request)
    maximum_no_of_days_to_generate_no_repeat = get_maximum_no_of_days_no_repeat(request)
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
    all_meals = MealsList.objects.filter(user=request.user)
    meal_options = MealsList.objects.filter(user=request.user).values('meal_option_id').distinct()
    meals = MealsList.objects.select_related('meal').filter(user=request.user)
    calories_total = 0
    protein_total = 0
    fat_total = 0
    carb_total = 0
    calories = 0
    protein = 0
    fat = 0
    carb = 0
    for meal in meals:
        try:
            one_meal = Meal.objects.get(id=meal.meal_id)
        except Exception:
            one_meal = None
        ingredients = MealIngredient.objects.select_related('ingredient_id').filter(meal_id=one_meal)
        for ingr in ingredients:
            ingr_obj = get_object_or_404(Ingredient, pk=ingr.ingredient_id.id)
            calories += (ingr.quantity / 100) * int(ingr_obj.calories_per_100_gram)
            protein += (ingr.quantity / 100) * int(ingr_obj.protein_per_100_gram)
            fat += (ingr.quantity / 100) * int(ingr_obj.fat_per_100_gram)
            carb += (ingr.quantity / 100) * int(ingr_obj.carbohydrates_per_100_gram)
            calories_total += calories
            protein_total += protein
            fat_total += fat
            carb_total += carb
            calories = 0
            protein = 0
            fat = 0
            carb = 0
    print('------', calories_total)

    try:
        meals_list_length = int(len(all_meals) / len(meal_options))
        average_clories_per_day = int(calories_total / meals_list_length)
        average_protein_per_day = int(protein_total / meals_list_length)
        average_fat_per_day = int(fat_total / meals_list_length)
        average_carb_per_day = int(carb_total / meals_list_length)
    except ZeroDivisionError:
        meals_list_length = 0
        average_clories_per_day = 0
        average_protein_per_day =0
        average_carb_per_day = 0
        average_fat_per_day = 0

    context = {
        'meals_list': meals_list,
        'user_meals_options': user_meals_options,
        'generated_user_meals_options': generated_user_meals_options,
        'day_meal_option_meal_list': day_meal_option_meal_list,
        'maximum_no_of_days_to_generate': maximum_no_of_days_to_generate,
        'maximum_no_of_days_to_generate_default': maximum_no_of_days_to_generate * 2,
        'in_meals_list': in_meals_list,
        'first_day_input_list': first_day_input_list,
        'option_meals_dict': option_meals_dict,
        'maximum_no_of_days_to_generate_no_repeat': maximum_no_of_days_to_generate_no_repeat,
        'average_clories_per_day': average_clories_per_day,
        'average_protein_per_day': average_protein_per_day,
        'average_fat_per_day': average_fat_per_day,
        'average_carb_per_day': average_carb_per_day,
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
        meals_in_meals_options = Meal.objects.filter(meal_option=meals_options[i]).order_by('name')
        meals = []
        for meal in meals_in_meals_options:
            ingredients = MealIngredient.objects.select_related('ingredient_id').filter(meal_id=meal.id)
            calories = 0
            protein = 0
            fat = 0
            carbohydrates = 0
            for ingr in ingredients:
                ingr_obj = get_object_or_404(Ingredient, pk=ingr.ingredient_id.id)
                calories += (ingr.quantity) / 100 * int(ingr_obj.calories_per_100_gram)
                protein += (ingr.quantity / 100) * int(ingr_obj.protein_per_100_gram)
                fat += (ingr.quantity / 100) * int(ingr_obj.fat_per_100_gram)
                carbohydrates += (ingr.quantity / 100) * int(ingr_obj.carbohydrates_per_100_gram)
            meals.append([meal, [round(calories), round(protein), round(fat), round(carbohydrates)]])
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
    current_meals_list = MealsList.objects.filter(user=request.user)
    current_meals = []
    for item in (list(current_meals_list)):
        if item.meal_id:
            meal = get_object_or_404(Meal, pk=item.meal_id)
            current_meals.append(meal)

    if append_existing:
        days = appended_days_generator(request.user, first_day, int(how_many_days))
    else:
        current_meals_list.delete()
        days = days_generator(first_day, int(how_many_days))

    for option in user_meals_options:
        option_meals_list = []
        meals_in_option = Meal.objects.filter(meal_option=option, user=request.user, special=0)
        meal_option = get_object_or_404(MealOption, pk=option, user=request.user)

        for meal in meals_in_option:
            if no_repetition:
                if meal not in current_meals:
                    option_meals_list.append(meal)
            else:
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

        if empty_meals_list:
            for k in range(len(random_meals_list)):
                new_meals_list = MealsList(day=days[k], meal_id=None, meal_option_id=meal_option.id,
                                           user_id=request.user.id)
                new_meals_list.save()
        else:
            for k in range(len(random_meals_list)):
                new_meals_list = MealsList(day=days[k], meal_id=random_meals_list[k].id, meal_option_id=meal_option.id,
                                           user_id=request.user.id)
                new_meals_list.save()
    return redirect('meals:index')


@require_POST
def update_meals_list(request):
    record_id = request.POST['record_id']
    to_update = request.POST['to_update']

    MealsList.objects.filter(pk=int(record_id)).update(meal_id=to_update)
    return redirect('meals:index')


def delete_meal_option(request, meal_option_id):
    MealOption.objects.filter(pk=meal_option_id).delete()
    return redirect('meals:edit_meals')


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
        ingr_obj = get_object_or_404(Ingredient, pk=ingr.ingredient_id.id)
        calories += (ingr.quantity) / 100 * int(ingr_obj.calories_per_100_gram)
        protein += (ingr.quantity) / 100 * int(ingr_obj.protein_per_100_gram)
        fat += (ingr.quantity) / 100 * int(ingr_obj.fat_per_100_gram)
        carbohydrates += (ingr.quantity) / 100 * int(ingr_obj.carbohydrates_per_100_gram)
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


def add_recipe(request, meal_id):
    recipe = request.POST['update_recipe_textarea']
    Meal.objects.filter(pk=meal_id).update(recipe=recipe)
    return redirect('meals:edit_meal_ingredients', meal_id=meal_id)


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
    MealsList.objects.filter(user=request.user).delete()
    return redirect('meals:index')


def update_meal_option(request, meal_option_id):
    new_name = request.POST['new_meal_option_name']
    MealOption.objects.filter(pk=meal_option_id).update(meal_option=new_name)
    return redirect('meals:edit_meals')


def update_meal_name(request, meal_id):
    new_meal_name = request.POST['new_meal_name']
    edit_special = request.POST.get('edit_special', False)
    print(edit_special)
    if edit_special == 'true':
        edit_special = True
    else:
        edit_special = False
    Meal.objects.filter(pk=meal_id).update(name=new_meal_name, special=edit_special)
    return redirect('meals:edit_meal_ingredients', meal_id=meal_id)


def generate_shopping_lists(request):
    meals = MealsList.objects.filter(user=request.user)
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
        if meal.meal_id:
            meal_instance = get_object_or_404(Meal, pk=meal.meal_id)
            for ingredient in MealIngredient.objects.filter(meal_id=meal_instance):
                ingredients_list.append(ingredient)

    for ingredient in ingredients_list:
        ingredient_object = get_object_or_404(Ingredient, pk=ingredient.ingredient_id_id)

    for shop in shops:
        for ingredient in ingredients_list:
            ingredient_object = get_object_or_404(Ingredient, pk=ingredient.ingredient_id_id)
            shop_id = ingredient_object.shop_id
            try:
                id = shop.id
            except Exception:
                id = None
            if id == shop_id:
                if ingredient_object in ingr_qt_dict.keys():
                    qt = ingr_qt_dict[ingredient_object][0]
                    qt += ingredient.quantity
                    ingr_qt_dict[ingredient_object] = [qt, ingredient_object.weight_per_unit]
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
            for shopping_item, qt in shoping_list_items.items():
                if qt[1] != 0:
                    unit = 1
                else:
                    unit = 2
                new_list_position = Products(product_name=shopping_item, quantity=qt[0],
                                             shopping_list_id_id=new_shopping_list.id,
                                             unit_id=unit)
                new_list_position.save()
    return redirect('shopping:shopping_list_index')


def delete_selected_days(request):
    meals_list_positions_to_delete_list = request.POST.getlist('mealsListPosition')
    for item in meals_list_positions_to_delete_list:
        MealsList.objects.filter(user=request.user, pk=item).delete()
    return redirect('meals:index')


def edit_ingredients(request):
    user_ingredients = Ingredient.objects.filter(user=request.user).order_by('name')
    user_shops = Shop.objects.filter(user=request.user.id)
    form = IngredientForm()
    context = {
        'user_ingredients': user_ingredients,
        'user_shops': user_shops,
        'form': form,
        'active_tab': 'shop',
    }
    return render(request, 'meals/ingredients_edit.html', context)


def add_shop(request):
    new_shop_name = request.POST['new_shop_name']
    new_shop_name = new_shop_name.upper()
    new_shop = Shop(name=new_shop_name, user=request.user)
    new_shop.save()
    return redirect('/ingredientsEdit#shops')


def edit_shop(request):
    print(request.POST)
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
                                weight_per_unit=avg_unit, shop=shop)
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

    edited_ingredient = Ingredient.objects.get(pk=ingr_id)
    edited_ingredient.name = new_ingredient_name
    edited_ingredient.calories_per_100_gram = kcal
    edited_ingredient.protein_per_100_gram = prot
    edited_ingredient.fat_per_100_gram = fat
    edited_ingredient.carbohydrates_per_100_gram = carb
    edited_ingredient.weight_per_unit = avg_unit
    edited_ingredient.shop = shop
    edited_ingredient.save()

    return redirect('meals:edit_ingredients')
