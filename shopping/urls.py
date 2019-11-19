from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'shopping'
urlpatterns = [
    path('shopping', views.shopping_list_index, name='shopping_list_index'),
]