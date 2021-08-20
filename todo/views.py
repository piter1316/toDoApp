from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from cars.models import Car
from meals.models import MealsList, MealIngredient, Meal, Ingredient
from shopping.models import ShoppingList, Products
from .forms import TodoForm
from .models import Todo


@login_required(login_url='/accounts/login')
def index(request):
    todo_list = Todo.objects.filter(user=request.user).order_by('id')

    form = TodoForm()
    context = {'todo_list': todo_list, 'form': form}
    return render(request, 'todo/toDo.html', context)


@require_POST
def addTodo(request):
    form = TodoForm(request.POST)

    if form.is_valid():
        new_todo = Todo(text=request.POST['text'], user=request.user)
        new_todo.save()

    return redirect('todo:index')


def completeTodo(request, todo_id):
    todo = Todo.objects.get(pk=todo_id)
    todo.complete = True
    todo.save()

    return redirect('todo:index')


def deleteCompleted(request):
    Todo.objects.filter(complete__exact=True, user=request.user).delete()

    return redirect('todo:index')


def deleteAll(request):
    Todo.objects.filter(user=request.user).delete()
    return redirect('todo:index')


def home(request):
    if request.user.is_authenticated:
        all_to_do_count = Todo.objects.filter(user=request.user, complete=False)
        all_meals = MealsList.objects.filter(user=request.user)
        meal_options = MealsList.objects.filter(user=request.user).values('meal_option_id').distinct()
        meals = MealsList.objects.select_related('meal').filter(user=request.user)
        cars_owned = Car.objects.filter(user=request.user, sold=0)
        cars_sold = Car.objects.filter(user=request.user, sold=1)
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

        try:
            meals_list_length = int(len(all_meals) / len(meal_options))
            average_clories_per_day = int(calories_total/meals_list_length)
            average_protein_per_day = int(protein_total/meals_list_length)
            average_fat_per_day = int(fat_total/meals_list_length)
            average_carb_per_day = int(carb_total/meals_list_length)
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
        distinct_meals =[]
        for meal in meals:
            if meal.meal:
                if meal.meal.name not in distinct_meals:
                    distinct_meals.append(meal.meal.name)


        context = {
            'all_to_do_count': len(all_to_do_count),
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
        }
    else:
        context = {}
    return render(request, 'todo/home.html', context)


