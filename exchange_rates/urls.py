from django.urls import path
from . import views

urlpatterns = [
    path('exchange_rates', views.exchange_rates, name='exchange_rates'),
]
