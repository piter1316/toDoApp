from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'shopping'
urlpatterns = [
    path('shopping', views.shopping_list_index, name='shopping_list_index'),
    path('shopping/add', views.add_shopping_list, name='add'),
    path('shopping/delete_all_shopping_lists', views.delete_all_shopping_lists, name='delete_all_shopping_lists'),
    path('shopping/add/product/<shopping_list_id>', views.add_product, name='add_product'),
    path('shopping/update_product/<product_id>', views.update_product, name='update_product'),
    path('shopping/delete/<shopping_list_id>', views.delete_shopping_list, name='delete'),
    path('shopping/bought/<id>', views.bought, name='bought'),
    path('shopping/bought_many', views.bought_many, name='bought_many'),
    path('shopping/delete_bought/<shopping_list_id>', views.delete_bought, name='delete_bought'),
    path('shopping/purge_list/<shopping_list_id>', views.purge_list, name='purge_list'),
    path('shopping/shopping_list_edit/<shopping_list_id>', views.shopping_list_edit, name='shopping_list_edit'),
]