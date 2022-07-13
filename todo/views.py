import datetime
import time
import pytz
from meals.views import get_today
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from cars.models import Car
from receipts.models import Receipt
from meals.models import MealsList, MealIngredient, Meal, Ingredient
from shopping.models import ShoppingList, Products
from .forms import TodoForm
from .models import Todo, TodoTodostep, ToDoMain


def get_all_to_do(user):
    todo_list_dict = {}
    main_todos = ToDoMain.objects.filter(user=user).order_by('id')
    for main_todo in main_todos:
        todo_list = Todo.objects.filter(to_do_main=main_todo)
        second_level = {}
        for element in todo_list:
            steps = TodoTodostep.objects.filter(todo=element)
            second_level[element] = [step for step in steps]
        todo_list_dict[main_todo] = second_level
    count = 0
    for k, v in todo_list_dict.items():
        if v.items():
            for k2, v2 in v.items():
                count += 1
    return count


@login_required(login_url='/accounts/login')
def index(request):
    todo_list_dict = {}
    main_todos = ToDoMain.objects.filter(user=request.user).order_by('id')
    for main_todo in main_todos:
        todo_list = Todo.objects.filter(to_do_main=main_todo)
        second_level = {}
        for element in todo_list:
            steps = TodoTodostep.objects.filter(todo=element)
            second_level[element] = [step for step in steps]
        todo_list_dict[main_todo] = second_level
    form = TodoForm()
    context = {'todo_list': todo_list_dict, 'form': form}
    return render(request, 'todo/toDo.html', context)


@require_POST
def add_todo_list(request):
    form = TodoForm(request.POST)
    if form.is_valid():
        new_todo = ToDoMain(name=request.POST['text'], user=request.user)
        new_todo.save()

    return redirect('todo:index')


def add_todo(request, list_id):
    to_do_name = request.POST.get('text')
    new_todo = Todo(text=to_do_name, to_do_main_id=list_id)
    new_todo.save()
    return redirect('todo:index')


def add_step(request, to_do_id):
    step_text = request.POST.get('addStep_' + str(to_do_id))
    new_step = TodoTodostep(todo_id=to_do_id, text=step_text)
    new_step.save()
    return redirect('todo:index')


def delete_main_list(request, list_id):
    ToDoMain.objects.filter(user_id=request.user, pk=list_id).delete()
    return redirect('todo:index')


def complete_todo(request, todo_id):
    todo = Todo.objects.get(pk=todo_id)
    todo.complete = True
    todo.save()
    return redirect('todo:index')


def delete_completed(request):
    Todo.objects.filter(complete__exact=True, user=request.user).delete()

    return redirect('todo:index')


def delete_all(request):
    Todo.objects.filter(user=request.user).delete()
    return redirect('todo:index')


@login_required(login_url='/accounts/login')
def home(request):
    if request.user.is_authenticated:
        all_to_do_count = get_all_to_do(request.user)
        meal_options = MealsList.objects.filter(user=request.user).values('meal_option_id').distinct()
        meals = MealsList.objects.select_related('meal').filter(user=request.user, )
        cars_owned = Car.objects.filter(user=request.user, sold=0)
        cars_sold = Car.objects.filter(user=request.user, sold=1)
        receipts = Receipt.objects.filter(user=request.user)
        receipts_dict = {
            'all': receipts,
            'with_warranty': [receipt for receipt in receipts if int(receipt.warranty_left) > 0],
            'without_warranty': [receipt for receipt in receipts if int(receipt.warranty_left) == 0]
        }
        calories_total = 0
        protein_total = 0
        fat_total = 0
        carb_total = 0
        calories = 0
        protein = 0
        fat = 0
        carb = 0
        today = get_today().date()
        todays_meals = []
        day_calories = 0
        day_protein = 0
        day_fat = 0
        day_carb = 0

        for meal in meals:
            try:
                if meal.day.split('_')[1] == str(today):
                    todays_meals.append(meal)
            except:
                pass

            ingredients = list(MealIngredient.objects.select_related('ingredient_id').filter(meal_id=meal.meal_id))
            if meal.extras:
                extra_ingredients = MealIngredient.objects.select_related('ingredient_id').filter(
                    meal_id=meal.extras.id)
                ingredients.extend(extra_ingredients)
            for ingr in ingredients:
                calories += (ingr.quantity / 100) * int(ingr.ingredient_id.calories_per_100_gram)
                protein += (ingr.quantity / 100) * int(ingr.ingredient_id.protein_per_100_gram)
                fat += (ingr.quantity / 100) * int(ingr.ingredient_id.fat_per_100_gram)
                carb += (ingr.quantity / 100) * int(ingr.ingredient_id.carbohydrates_per_100_gram)
                if meal.current:
                    calories_total += calories
                    protein_total += protein
                    fat_total += fat
                    carb_total += carb
                if meal.day.split('_')[1] == str(today):
                    day_calories += calories
                    day_protein += protein
                    day_fat += fat
                    day_carb += carb
                calories = 0
                protein = 0
                fat = 0
                carb = 0
        todays_macro = (round(day_calories, 0), round(day_protein, 0), round(day_fat, 0), round(day_carb, 0))
        # todays_meals[meal.meal_option] = todays_meals[meal.meal_option].append(calories)

        try:
            meals_list_length = int(len(meals.filter(current=1)) / len(meal_options))
            average_clories_per_day = int(calories_total / meals_list_length)
            average_protein_per_day = int(protein_total / meals_list_length)
            average_fat_per_day = int(fat_total / meals_list_length)
            average_carb_per_day = int(carb_total / meals_list_length)
        except ZeroDivisionError:
            meals_list_length = 0
            average_clories_per_day = 0
            average_protein_per_day = 0
            average_fat_per_day = 0
            average_carb_per_day = 0

        shopping_lists = ShoppingList.objects.filter(user_id=request.user)
        products_to_buy_counter = 0
        for product in shopping_lists:
            for item in Products.objects.filter(shopping_list_id=product, bought=False):
                products_to_buy_counter += 1
        distinct_meals = []
        for meal in meals:
            if meal.current:
                if meal.meal:
                    if meal.meal.name not in distinct_meals:
                        distinct_meals.append(meal.meal.name)
                if meal.extras:
                    if meal.extras not in distinct_meals:
                        distinct_meals.append(meal.extras)
        context = {
            'all_to_do_count': all_to_do_count,
            'meals_list_length': meals_list_length,
            'meals': len(distinct_meals),
            'meal_options': len(meal_options),
            'shopping_lists': len(shopping_lists),
            'cars_owned': cars_owned,
            'cars_sold': cars_sold,
            'products_to_buy_counter': products_to_buy_counter,
            'average_clories_per_day': average_clories_per_day,
            'average_protein_per_day': average_protein_per_day,
            'average_fat_per_day': average_fat_per_day,
            'average_carb_per_day': average_carb_per_day,
            'todays_macro': todays_macro,
            'todays_meals': todays_meals,
            'today': today,
            'receipts': receipts_dict,
        }
    else:
        context = {}
    return render(request, 'todo/home.html', context)
