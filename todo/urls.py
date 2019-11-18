from django.urls import path
from . import views
urlpatterns = [
    path('', views.login, name='login'),
    path('toDo', views.index, name='index'),
    path('add', views.addTodo, name='add'),
    path('complete/<todo_id>', views.completeTodo, name='complete'),
    path('deletecomplete', views.deleteCompleted, name='deletecomplete'),
    path('deleteAll', views.deleteAll, name='deleteAll'),
]