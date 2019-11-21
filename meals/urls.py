from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'todo'
urlpatterns = [
    path('', views.home, name='home'),
    path('toDo', views.index, name='index'),
    path('add', views.addTodo, name='add'),
    path('complete/<todo_id>', views.completeTodo, name='complete'),
    path('deletecomplete', views.deleteCompleted, name='deletecomplete'),
    path('deleteAll', views.deleteAll, name='deleteAll'),
]