from django.shortcuts import render
from django.http import HttpResponse
import requests
# Create your views here.


def exchange_rates(request):
    nbp_api_request = requests.get('https://api.nbp.pl/api/exchangerates/tables/A?format=json')
    npb_exchange_rates = nbp_api_request.json()
    exchange_rate_date = npb_exchange_rates[0]['effectiveDate']
    all_rates = npb_exchange_rates[0]['rates']
    # user_saved_currencies = []
    user_rates_to_render = []
    for rate in all_rates:
        # if rate.get('code') in user_saved_currencies:
        user_rates_to_render.append(rate)
    return render(request, 'exchange_rates/exchange_rates.html', {'user_rates_to_render': user_rates_to_render})
