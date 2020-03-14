from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from meals.models import MealsList
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
        calories_total = 0

        try:
            meals_list_length = int(len(all_meals) / len(meal_options))
            average_clories_per_day = int(calories_total/meals_list_length)
        except ZeroDivisionError:
            meals_list_length = 0
            average_clories_per_day = 0
        shopping_lists = ShoppingList.objects.filter(user_id=request.user)
        products_to_buy_counter = 0
        for product in shopping_lists:
            for item in Products.objects.filter(shopping_list_id=product, bought=False):
                products_to_buy_counter += 1
        distinct_meals =[]
        for meal in meals:
            if meal.meal.name not in distinct_meals:
                distinct_meals.append(meal.meal.name)

        context = {
            'all_to_do_count': len(all_to_do_count),
            'meals_list_length': meals_list_length,
            'meals': len(distinct_meals),
            'meal_options': len(meal_options),
            'shopping_lists': len(shopping_lists),
            'products_to_buy_counter': products_to_buy_counter,
            'average_clories_per_day': average_clories_per_day
        }
    else:
        context = {}
    return render(request, 'todo/home.html', context)


