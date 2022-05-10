from django.urls import path
from . import views

app_name = 'exchange_rates'
urlpatterns = [
    path('exchange_rates', views.exchange_rates, name='exchange_rates'),
    path('exchange_rates/<currency>', views.exchange_rates_diagram, name='exchange_rates_diagram'),
]
