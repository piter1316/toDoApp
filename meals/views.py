import random
from django.contrib import messages

from django.db.models import Q, Count, Prefetch
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from django.views.decorators.http import require_POST

from meals.forms import MealForm, IngredientForm, MealOptionForm
from meals.models import MealOption, Meal, Ingredient, MealsList, Week, Unit, MealIngredient, Shop, ProductDivision, \
    is_hi_protein, VEGIES_OUT
from shopping.models import ShoppingList, Products
import time
import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def average_for_whole_list(meals_list, generated_user_meals_options, user, current, meal_ingredients_dict):
    all_meals = meals_list
    meal_options = generated_user_meals_options
    meals = MealsList.objects.select_related('meal').filter(user=user, current=current)
    ingredients_total = []
    tmp_extra_total = []
    calories_total = 0
    protein_total = 0
    fat_total = 0
    carb_total = 0
    vegies_total = 0
    fruits_total = 0
    calories = 0
    protein = 0
    fat = 0
    carb = 0
    vegies = 0
    fruits = 0
    average_vegies_per_day = 0
    average_fruits_per_day = 0

    for meal in meals:
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
            if 'warzywa' in ingr.ingredient_id.division.division_name.lower() and ingr.name.lower() not in VEGIES_OUT:
                vegies += ingr.quantity
            if 'owoce' in ingr.ingredient_id.division.division_name.lower():
                fruits += ingr.quantity
            calories += (ingr.quantity / 100) * int(ingr.calories_per_100_gram)
            protein += (ingr.quantity / 100) * int(ingr.protein_per_100_gram)
            fat += (ingr.quantity / 100) * int(ingr.fat_per_100_gram)
            carb += (ingr.quantity / 100) * int(ingr.carbohydrates_per_100_gram)
            calories_total += calories
            protein_total += protein
            fat_total += fat
            carb_total += carb
            vegies_total += vegies
            fruits_total += fruits
            calories = 0
            protein = 0
            fat = 0
            carb = 0
            vegies = 0
            fruits = 0

        for item in tmp_extra_total:
            if item in ingredients_total:
                ingredients_total.remove(item)

    try:
        meals_list_length = int(len(all_meals) / len(meal_options))
        average_clories_per_day = int(calories_total / meals_list_length)
        average_protein_per_day = int(protein_total / meals_list_length)
        average_fat_per_day = int(fat_total / meals_list_length)
        average_carb_per_day = int(carb_total / meals_list_length)
        average_vegies_per_day = int(vegies_total / meals_list_length)
        average_fruits_per_day = int(fruits_total / meals_list_length)
    except ZeroDivisionError:
        meals_list_length = 0
        average_clories_per_day = 0
        average_protein_per_day = 0
        average_carb_per_day = 0
        average_fat_per_day = 0
    return (average_clories_per_day, average_protein_per_day, average_carb_per_day, average_fat_per_day,
            average_vegies_per_day, average_fruits_per_day)


def get_today():
    return datetime.datetime.now()


def days_generator(first, how_many):
    days = ['PN', 'WT', 'ŚR', 'CZW', 'PT', 'SB', 'ND']
    days_list = []
    itr = ''
    space = ''
    first_date = datetime.datetime.strptime(first[1], '%Y-%m-%d').date()
    first = first[0]
    for i in range(how_many):
        days_list.append(days[first] + space + str(itr) + '_' + str(first_date + datetime.timedelta(days=i)))
        first += 1
        if first == len(days):
            first = 0
    return days_list


def appended_days_generator(request, first, how_many):
    days = ['PN', 'WT', 'ŚR', 'CZW', 'PT', 'SB', 'ND']
    days_list = []
    meals_list_ids = MealsList.objects.filter(user_id=request, current=1)
    itr = meals_list_ids.reverse()[0].id
    space = '_'
    first_date = datetime.datetime.strptime(first[1], '%Y-%m-%d').date()
    first = first[0]
    for i in range(how_many):
        days_list.append(days[first] + '_' + str(first_date + datetime.timedelta(days=i)))
        first += 1
        if first == len(days):
            first = 0
    return days_list


def get_max_days(request, exclude_current=False):
    # 1. Przygotowujemy filtr dla posiłków
    # Podstawowe warunki: ten sam użytkownik i nie "specjalne"
    meal_filter = Q(meal__user=request.user, meal__special=0)

    # 2. Jeśli chcemy "no_repeat", dodajemy warunek wykluczający
    if exclude_current:
        excluded_ids = MealsList.objects.filter(
            user=request.user,
            current=1,
            meal_id__isnull=False
        ).values_list('meal_id', flat=True)

        meal_filter &= ~Q(meal__id__in=excluded_ids)

    # 3. Jedno zapytanie z agregacją
    counts = MealOption.objects.filter(
        user=request.user,
        is_taken_to_generation=1
    ).annotate(
        total=Count('meal', filter=meal_filter)
    ).values_list('total', flat=True)

    return min(counts) if counts else 0


@login_required(login_url='/accounts/login')
def meals(request, current=1):
    today_to_template = get_today().date()
    start = time.time()
    in_meals_list = True
    current = int(current)
    user = request.user

    # 1. Pobieramy opcje
    user_meals_options = MealOption.objects.filter(user=user).order_by('position')
    user_meals_options_gen = MealOption.objects.filter(user=user, is_taken_to_generation=1).order_by('position')
    # 2. Pobieramy listę (MealsList) złączoną (JOIN) z modelami Meal i Extras
    # Używamy select_related dla szybkości
    meals_list_qs = MealsList.objects.filter(user=user, current=current).select_related(
        'meal', 'meal_option', 'extras'
    ).order_by('day', 'meal_option__position')

    generated_user_meals_options = MealsList.objects.filter(user=user, current=current).order_by(
        'meal_option__position').values(
        'meal_option__meal_option', 'meal_option_id').distinct()

    # 3. Słownik wszystkich posiłków zoptymalizowany pod listę rozwijaną
    # POBIERAMY TYLKO RAZ Z BAZY
    # UWAGA: Zakładam, że masz uzupełnione pola total_kcal, is_hi_protein_flag, has_short_expiry_flag
    # Jeśli na razie są puste, kod zadziała, ale pokaże "0 kcal".
    all_meals_for_dropdown = Meal.objects.filter(user=user).values(
        'id', 'name', 'meal_option_id', 'special', 'total_kcal', 'has_short_expiry_flag', 'is_hi_protein_flag'
    )

    meals_by_option = {}
    for m in all_meals_for_dropdown:
        opt_id = m['meal_option_id']
        if opt_id not in meals_by_option:
            meals_by_option[opt_id] = []
        meals_by_option[opt_id].append({
            'id': m['id'],
            'name': m['name'],
            'kcal': round(m['total_kcal']) if m['total_kcal'] else 0,
            'special': m['special'],
            'short_expiry': m['has_short_expiry_flag'],
            'hi_protein': m['is_hi_protein_flag']
        })

    for opt_id in meals_by_option:
        meals_by_option[opt_id].sort(key=lambda x: x['name'])

    all_meals_in_option_dict = {}
    for option in user_meals_options:
        all_meals_in_option_dict[option] = meals_by_option.get(option.id, [])

    # 4. Przetwarzanie struktury dla Template'u
    days_data = []
    current_day_str = None
    current_day_dict = None

    total_list_kcal = total_list_prot = total_list_fat = total_list_carb = total_list_vegies = total_list_fruits = 0
    days_set = set()

    for item in meals_list_qs:
        day_str = item.day
        days_set.add(day_str)

        # Jeśli zaczyna się nowy dzień, stwórz dla niego słownik
        if current_day_str != day_str:
            if current_day_dict:
                days_data.append(current_day_dict)

            day_parts = day_str.split('_')  # np. ['Piątek', '2026-03-13']
            day_name = day_parts[0] if len(day_parts) > 0 else ''
            day_date = day_parts[1] if len(day_parts) > 1 else ''

            current_day_dict = {
                'raw_day': day_str,
                'day_name': day_name,
                'day_date': day_date,
                'is_today': str(today_to_template) == day_date,
                'meals': [],
                'totals': {'kcal': 0, 'prot': 0, 'fat': 0, 'carb': 0, 'vegies': 0, 'fruits': 0}
            }
            current_day_str = day_str

        # Przetwarzanie pojedynczego wpisu z MealsList
        meal_obj = item.meal
        extras_obj = item.extras
        # Inicjalizacja danych dla pojedynczej "komórki" w tabeli
        total_macro = int(meal_obj.total_carb) if meal_obj else 0 + int(
            meal_obj.total_fat) if meal_obj else 0 + int(meal_obj.total_protein) if meal_obj else 0
        try:
            b_precent = int(meal_obj.total_protein) if meal_obj else 0 / total_macro
        except ZeroDivisionError:
            b_precent = 0

        try:
            t_precent = int(meal_obj.total_fat) if meal_obj else 0 / total_macro
        except ZeroDivisionError:
            t_precent = 0

        try:
            w_precent = int(meal_obj.total_carb) if meal_obj else 0 / total_macro
        except ZeroDivisionError:
            w_precent = 0

        extras_total_macro = int(extras_obj.total_carb) if extras_obj else 0 + int(
            extras_obj.total_fat) if extras_obj else 0 + int(extras_obj.total_protein) if extras_obj else 0
        try:
            extras_b_precent = int(extras_obj.total_protein) if extras_obj else 0 / extras_total_macro
        except ZeroDivisionError:
            extras_b_precent = 0

        try:
            extras_t_precent = int(extras_obj.total_fat) if extras_obj else 0 / extras_total_macro
        except ZeroDivisionError:
            extras_t_precent = 0

        try:
            extras_w_precent = int(extras_obj.total_carb) if extras_obj else 0 / extras_total_macro
        except ZeroDivisionError:
            extras_w_precent = 0
        cell_data = {
            'list_id': item.id,
            'option_name': item.meal_option.meal_option,
            'option_id': item.meal_option_id,
            'kcal': int(meal_obj.total_kcal) if meal_obj else None,
            'b': int(meal_obj.total_protein) if meal_obj else None,
            'b_precent': b_precent,
            't_precent': t_precent,
            'w_precent': w_precent,
            't': int(meal_obj.total_fat) if meal_obj else None,
            'w': int(meal_obj.total_carb) if meal_obj else None,
            'total_macro': total_macro,
            'extras_total_macro': extras_total_macro,
            'meal_id': meal_obj.id if meal_obj else None,
            'meal_name': meal_obj.name if meal_obj else "-----------------------",
            'is_special': meal_obj.special if meal_obj else False,
            'short_expiry': meal_obj.has_short_expiry_flag if meal_obj else False,
            'extras_id': extras_obj.id if extras_obj else None,
            'extras_name': extras_obj.name if extras_obj else None,
            'extras_kcal': int(extras_obj.total_kcal) if extras_obj else None,
            'extras_b': int(extras_obj.total_protein) if extras_obj else None,
            'extras_t': int(extras_obj.total_fat) if extras_obj else None,
            'extras_w': int(extras_obj.total_carb) if extras_obj else None,
            'extras_short_expiry': extras_obj.has_short_expiry_flag if extras_obj else False,
            'dropdown_options': all_meals_in_option_dict.get(item.meal_option, [])
        }

        # Makro posiłku głównego
        m_kcal = 0
        m_prot = 0
        m_fat = 0
        m_carb = 0
        m_veg = 0
        m_fru = 0
        if meal_obj:
            m_kcal = meal_obj.total_kcal or 0
            m_prot = meal_obj.total_protein or 0
            m_fat = meal_obj.total_fat or 0
            m_carb = meal_obj.total_carb or 0
            m_veg = meal_obj.total_vegies or 0
            m_fru = meal_obj.total_fruits or 0

            # Dodaj makro dodatków
        if extras_obj:
            m_kcal += extras_obj.total_kcal or 0
            m_prot += extras_obj.total_protein or 0
            m_fat += extras_obj.total_fat or 0
            m_carb += extras_obj.total_carb or 0
            m_veg += extras_obj.total_vegies or 0
            m_fru += extras_obj.total_fruits or 0

            # Sumowanie makro dnia
        current_day_dict['totals']['kcal'] += m_kcal
        current_day_dict['totals']['prot'] += m_prot
        current_day_dict['totals']['fat'] += m_fat
        current_day_dict['totals']['carb'] += m_carb
        current_day_dict['totals']['vegies'] += m_veg
        current_day_dict['totals']['fruits'] += m_fru

        current_day_dict['meals'].append(cell_data)

    # Dodajemy ostatni dzień po zakończeniu pętli
    if current_day_dict:
        days_data.append(current_day_dict)

    # Sumowanie średnich dla wszystkich dni
    for d in days_data:
        # Zaokrąglamy przed dodaniem do globalnej sumy (dla spójności)
        d['totals']['kcal'] = round(d['totals']['kcal'])
        d['totals']['prot'] = round(d['totals']['prot'])
        d['totals']['fat'] = round(d['totals']['fat'])
        d['totals']['carb'] = round(d['totals']['carb'])
        d['totals']['vegies'] = round(d['totals']['vegies'])
        d['totals']['fruits'] = round(d['totals']['fruits'])

        total_list_kcal += d['totals']['kcal']
        total_list_prot += d['totals']['prot']
        total_list_fat += d['totals']['fat']
        total_list_carb += d['totals']['carb']
        total_list_vegies += d['totals']['vegies']
        total_list_fruits += d['totals']['fruits']

    # Obliczanie średnich
    no_of_days = len(days_set) if days_set else 1
    average_clories_per_day = round(total_list_kcal / no_of_days)
    average_protein_per_day = round(total_list_prot / no_of_days)
    average_fat_per_day = round(total_list_fat / no_of_days)
    average_carb_per_day = round(total_list_carb / no_of_days)
    average_vegies_per_day = round(total_list_vegies / no_of_days)
    average_fruits_per_day = round(total_list_fruits / no_of_days)

    maximum_no_of_days_to_generate = get_max_days(request)
    maximum_no_of_days_to_generate_no_repeat = get_max_days(request, exclude_current=True)

    # Dni tygodnia
    first_day_input_list = {}
    days_of_the_week = list(Week.objects.all())
    today_weekday = get_today().weekday()
    if days_of_the_week:
        for i in range(7):
            idx = (today_weekday + i) % 7
            day_obj = days_of_the_week[idx]
            first_day_input_list[day_obj] = (
                get_today() + datetime.timedelta(days=i),
                [day_obj]
            )

    days_data = sorted(days_data, key=lambda x: x['day_date'])

    context = {
        'days_data': days_data,  # Zastępuje day_meal_option_meal_list
        'generated_user_meals_options': generated_user_meals_options,
        'average_clories_per_day': average_clories_per_day,
        'average_protein_per_day': average_protein_per_day,
        'average_fat_per_day': average_fat_per_day,
        'average_carb_per_day': average_carb_per_day,
        'average_vegies_per_day': average_vegies_per_day,
        'average_fruits_per_day': average_fruits_per_day,
        'current': current,
        'today_to_template': today_to_template,

        # Te poniżej zostawiam dla zachowania kompatybilności
        'meals_list': meals_list_qs,
        'maximum_no_of_days_to_generate': maximum_no_of_days_to_generate,
        'maximum_no_of_days_to_generate_default': maximum_no_of_days_to_generate * 2,
        'in_meals_list': in_meals_list,
        'first_day_input_list': first_day_input_list,
        'maximum_no_of_days_to_generate_no_repeat': maximum_no_of_days_to_generate_no_repeat,
        'all_meals_in_option_dict': all_meals_in_option_dict,
        'user_meals_options': user_meals_options_gen,
    }

    return render(request, 'meals/meals_list.html', context)


@login_required(login_url='/accounts/login')
def edit_meals(request):
    user = request.user

    form = MealForm(request.POST or None)
    form_ingredient = IngredientForm(request.POST or None)
    form_meal_option = MealOptionForm(request.POST or None)

    # 2. Pobieramy opcje posiłków
    meals_options = MealOption.objects.filter(user=user).order_by('position')
    units = Unit.objects.all()

    all_meals_qs = Meal.objects.filter(user=user).select_related('meal_option').prefetch_related(
        Prefetch(
            'mealingredient_set',
            queryset=MealIngredient.objects.select_related('ingredient_id__division')
        )
    ).order_by('name')

    meals_options_dict = {option: [] for option in meals_options}

    opt_map = {option.id: option for option in meals_options}

    for meal in all_meals_qs:
        option_obj = opt_map.get(meal.meal_option_id)
        if option_obj:
            macro_data = [
                round(meal.total_kcal or 0),
                round(meal.total_protein or 0),
                round(meal.total_fat or 0),
                round(meal.total_carb or 0),
                meal.is_hi_protein_flag
            ]
            meals_options_dict[option_obj].append([meal, macro_data])

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
    first_day = (int(request.POST['first_day'].split('|')[0]) - 1, request.POST['first_day'].split('|')[1])
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
        current_days = int(len(current_meals_list) / len(user_meals_options))

    else:
        previous_meals_list.delete()
        current_meals_list.update(current=0)
        days = days_generator(first_day, int(how_many_days))
        current_days = 0
    for option in user_meals_options:
        option_meals_list = []
        meals_in_option = Meal.objects.filter(meal_option=option, user=request.user, special=0)
        ingredients_with_short = MealIngredient.objects.select_related('meal_id').select_related(
            'ingredient_id').filter(ingredient_id__short_expiry=1, meal_id__meal_option_id=option)
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
    meal_obj = get_object_or_404(Meal, user_id=request.user, pk=meal_id)
    meal_list = [meal_obj]
    ingredients = MealIngredient.objects.filter(meal_id=meal_id).select_related('ingredient_id')
    user_ingredients = Ingredient.objects.filter(user=request.user).select_related('division').order_by('name')
    user_shops = Shop.objects.filter(user=request.user)
    units = Unit.objects.all()

    recipe_text = meal_obj.recipe or ""
    recipe_rows = recipe_text.count('\n') + 1 if recipe_text else 1

    context = {
        'meal': meal_list,
        'ingredients': ingredients,
        'units': units,
        'recipe_rows': recipe_rows,
        'user_ingredients': user_ingredients,
        'user_shops': user_shops,
        'calories': round(meal_obj.total_kcal),
        'protein': round(meal_obj.total_protein),
        'fat': round(meal_obj.total_fat),
        'carbohydrates': round(meal_obj.total_carb)
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

    ingredient = MealIngredient.objects.get(pk=ingredient_id)
    ingredient.quantity = new_quantity
    ingredient.save()
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
            new_list_position_list = []
            for shopping_item, qt in shoping_list_items.items():
                if qt[1] != 0:
                    unit = 1
                else:
                    unit = 2
                new_list_position = Products(product_name=shopping_item, quantity=qt[0],
                                             shopping_list_id_id=new_shopping_list.id,
                                             unit_id=unit, division_id=shopping_item.division)
                new_list_position_list.append(new_list_position)
            Products.objects.bulk_create(new_list_position_list)
    return redirect('shopping:shopping_list_index')


def delete_selected_days(request):
    meals_list_positions_to_delete_list = request.POST.getlist('mealsListPosition')
    for item in meals_list_positions_to_delete_list:
        MealsList.objects.filter(user=request.user, pk=item).delete()
    return redirect('/mealsList/1')


def edit_ingredients(request):
    user_ingredients = Ingredient.objects.filter(user=request.user).select_related('shop').order_by('name')
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


@login_required(login_url='/accounts/login')
def edit_ingredient_index(request, ingr_id):
    ingredient = Ingredient.objects.get(pk=ingr_id)
    return_url = (request.META.get('HTTP_REFERER'))
    context = {
        'ingredient': ingredient,
        'user_shops': Shop.objects.filter(user=request.user.id),
        'return_url': return_url,
        'user_divisions': ProductDivision.objects.filter(user=request.user).order_by('-priority'),
        'meals_with_ingredient': ingredient.meals_with_ingredient,
    }

    return render(request, 'meals/ingredient_edit.html', context)


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
    return_url = request.POST.get('return_url', False)
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
    if return_url:
        return redirect(return_url)
    else:
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
        new_division = ProductDivision(division_name=request.POST['division_name'],
                                       priority=request.POST['division_priority'], user_id=request.user.id)
        new_division.save()
    return redirect('/ingredientsEdit#division')


def delete_division(request, division_id):
    try:
        ProductDivision.objects.filter(pk=division_id, user_id=request.user.id).delete()
    except Exception as e:
        messages.error(request, 'Podany dział zawiera produkty i nie zostanie usuniety.')
    return redirect('/ingredientsEdit#division')


def edit_extras(request):
    extras_to_add = request.POST.get('extras_select', False)
    meals_list_id = request.POST.get('meals_list_position', False)
    if request.method == "POST":
        MealsList.objects.filter(pk=meals_list_id).update(extras=extras_to_add)
    return redirect('/mealsList/1')


def delete_extras(request, meals_list_id):
    MealsList.objects.filter(pk=meals_list_id).update(extras=None)
    return redirect('/mealsList/1')


def generate_shopping_list_for_meal(request, meal_id):
    portions = request.POST.get('portions')
    append_to_existing_shopping_lists = request.POST.get('append_to_existing_shopping_lists')
    meal_ingredients = MealIngredient.objects.select_related('ingredient_id').filter(meal_id_id=meal_id)
    meal_name = Meal.objects.filter(pk=meal_id)[0].name
    shop_dict = {}
    user_shops_query = Shop.objects.filter(user_id=request.user)
    existing_shopping_lists = {}

    for shopping_list in ShoppingList.objects.filter(user_id_id=request.user):
        existing_shopping_lists[shopping_list.id] = shopping_list.name
    for shop in user_shops_query:
        shop_dict[shop.id] = shop.name
    data_to_insert = []
    for ingredient in meal_ingredients:
        if ingredient.ingredient_id.weight_per_unit > 0:
            quantity = round(ingredient.quantity / ingredient.ingredient_id.weight_per_unit, 2)
            unit = 1
        else:
            quantity = ingredient.quantity
            unit = 2
        final_quantity = round(quantity * int(portions), 2)
        data_to_insert.append(
            {'ingredient': ingredient, 'quantity': final_quantity, 'unit': unit,
             'division': ingredient.ingredient_id.division, 'shop_id': shop_dict.get(ingredient.ingredient_id.shop_id)})
    if append_to_existing_shopping_lists:
        shopping_list_positions_dict = {}
        for position in data_to_insert:
            if position.get('shop_id'):
                for key, value in existing_shopping_lists.items():
                    if value == position.get('shop_id'):
                        if position.get('shop_id') not in shopping_list_positions_dict.keys():
                            shopping_list_positions_dict[existing_shopping_lists.get(key)] = Products.objects.filter(
                                shopping_list_id=key)
            else:
                for key, value in existing_shopping_lists.items():
                    if value == 'NIEPRZYPISANY':
                        if 'NIEPRZYPISANY' not in shopping_list_positions_dict.keys():
                            shopping_list_positions_dict[existing_shopping_lists.get(key)] = Products.objects.filter(
                                shopping_list_id=key)

        for position in data_to_insert:
            if position.get('shop_id'):
                shop_to_alter = position.get('shop_id')
            else:
                shop_to_alter = 'NIEPRZYPISANY'
            if shopping_list_positions_dict.get(shop_to_alter) is None:
                if shop_to_alter not in existing_shopping_lists.values():
                    new_shopping_list = ShoppingList(user_id=request.user, name=shop_to_alter, generated=1)
                    new_shopping_list.save()
                    new_product = Products(product_name=position.get('ingredient'), quantity=position.get('quantity'),
                                           shopping_list_id_id=new_shopping_list.id,
                                           unit_id=position.get('unit'), division_id=position.get('division'))
                    new_product.save()
                    existing_shopping_lists[new_shopping_list.id] = new_shopping_list.name
                    shopping_list_positions_dict[new_shopping_list.name] = Products.objects.filter(
                        product_name=position.get('ingredient'), shopping_list_id__name=new_shopping_list.name)
            else:
                shop_to_alter_id = next(k for k, v in existing_shopping_lists.items() if v == shop_to_alter)
                if str(position.get('ingredient')) in [str(item.product_name) for item in
                                                       shopping_list_positions_dict.get(shop_to_alter)]:
                    product_to_alter = Products.objects.filter(product_name=str(position.get('ingredient')),
                                                               shopping_list_id_id=shop_to_alter_id)[0]
                    product_to_alter.quantity = round(product_to_alter.quantity + float(position.get('quantity')), 2)
                    product_to_alter.save()
                else:
                    for k, v in existing_shopping_lists.items():
                        if shop_to_alter == v:
                            shop_to_alter = k
                    new_product = Products(product_name=position.get('ingredient'), quantity=position.get('quantity'),
                                           shopping_list_id_id=shop_to_alter,
                                           unit_id=position.get('unit'), division_id=position.get('division'))
                    new_product.save()
    else:
        new_shopping_list = ShoppingList(user_id=request.user, name=meal_name, generated=1)
        new_shopping_list.save()
        new_list_position_list = []
        for position in data_to_insert:
            position['shop_id'] = new_shopping_list.id
            new_list_position = Products(product_name=position.get('ingredient'), quantity=position.get('quantity'),
                                         shopping_list_id_id=position.get('shop_id'),
                                         unit_id=position.get('unit'), division_id=position.get('division'))
            new_list_position_list.append(new_list_position)
        Products.objects.bulk_create(new_list_position_list)
    return redirect('shopping:shopping_list_index')


def copy_meal(request, meal_id):
    meal_ingredients = MealIngredient.objects.filter(meal_id=meal_id)
    current_meal = Meal.objects.get(pk=meal_id)
    new_meal = Meal(user=request.user, meal_option=current_meal.meal_option, name=request.POST.get('copy_name'),
                    recipe=current_meal.recipe)
    new_meal.save()
    for ingr in meal_ingredients:
        new_meal_ingredient = MealIngredient(meal_id=new_meal, ingredient_id=ingr.ingredient_id, quantity=ingr.quantity)
        new_meal_ingredient.save()
    return redirect(reverse('meals:edit_meal_ingredients', kwargs={'meal_id': new_meal.pk}))
