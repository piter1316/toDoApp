from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'receipts'
urlpatterns = [
    path('receipts', views.receipts_home, name='receipts_home'), ]
