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
    path('archive_main_list/<list_id>', views.archive_main_list, name='archive_main_list'),
    path('restore_main_list_from_archive/<list_id>', views.restore_main_list_from_archive, name='restore_main_list_from_archive'),
    path('complete_todo/<todo_id>', views.complete_todo, name='complete_todo'),
    path('un_complete_todo/<todo_id>', views.un_complete_todo, name='un_complete_todo'),
    path('delete_todo/<todo_id>', views.delete_todo, name='delete_todo'),
    path('complete_step/<step_id>', views.complete_step, name='complete_step'),
    path('un_complete_step/<step_id>', views.un_complete_step, name='un_complete_step'),
    path('delete_step/<step_id>', views.delete_step, name='delete_step'),
    path('deletecomplete', views.delete_completed, name='deletecomplete'),
    path('delete_all', views.delete_all, name='delete_all'),

]