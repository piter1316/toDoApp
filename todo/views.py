from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Todo
from .forms import TodoForm
from django.views.decorators.http import require_POST


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


def login(request):
    context = {}
    return render(request, 'todo/home.html', context)
