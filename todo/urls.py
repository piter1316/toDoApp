from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'todo'
urlpatterns = [
    path('toDo', views.index, name='index'),
    path('add', views.add_todo_list, name='add'),
    path('add_todo/<list_id>', views.add_todo, name='add_todo'),
    path('addStep/<to_do_id>', views.add_step, name='add_step'),
    path('delete_main_list/<list_id>', views.delete_main_list, name='delete_main_list'),
    path('complete/<todo_id>', views.complete_todo, name='complete'),
    path('deletecomplete', views.delete_completed, name='deletecomplete'),
    path('delete_all', views.delete_all, name='delete_all'),

]