from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'shopping'
urlpatterns = [
    path('shopping', views.shopping_list_index, name='shopping_list_index'),
    path('shopping/add', views.add_shopping_list, name='add'),
    path('shopping/add/product/<shopping_list_id>', views.add_product, name='add_product'),
    path('shopping/delete/<shopping_list_id>', views.delete_shopping_list, name='delete'),
]