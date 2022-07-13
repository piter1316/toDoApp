from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'todo'
urlpatterns = [
    path('toDo', views.index, name='index'),
    path('add', views.add_todo, name='add'),
    path('complete/<todo_id>', views.complete_todo, name='complete'),
    path('deletecomplete', views.delete_completed, name='deletecomplete'),
    path('delete_all', views.delete_all, name='delete_all'),

]