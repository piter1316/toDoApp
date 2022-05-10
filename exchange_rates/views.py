from django.shortcuts import render
from django.http import HttpResponse
import requests
import datetime
import json


def get_rates_in_time(time, total_data):
    rates = []
    for rate in total_data:
        rates.append(rate)
        if rate['effectiveDate'] == str(time):
            break
        if rate['effectiveDate'] < str(time):
            break
    return json.dumps(list(reversed(rates)))


def get_all_currencies():
    nbp_api_request = requests.get('https://api.nbp.pl/api/exchangerates/tables/A?format=json')
    npb_exchange_rates = nbp_api_request.json()
    exchange_rate_date = npb_exchange_rates[0]['effectiveDate']
    all_rates = npb_exchange_rates[0]['rates']
    user_rates_to_render = []
    for rate in all_rates:
        user_rates_to_render.append(rate)
    return user_rates_to_render


def exchange_rates(request):
    context = {'user_rates_to_render': get_all_currencies()}
    return render(request, 'exchange_rates/exchange_rates.html', context)


def exchange_rates_diagram(request, currency):
    # https://api.nbp.pl/api/exchangerates/rates/a/gbp/2021-05-10/2022-05-10/?format=json

    today = datetime.date.today()
    week_back = today - datetime.timedelta(days=7)
    month_back = today - datetime.timedelta(days=30)
    two_months_back = today - datetime.timedelta(days=60)
    three_months_back = today - datetime.timedelta(days=90)
    six_months_back = today - datetime.timedelta(days=180)
    one_year_back = today - datetime.timedelta(days=365)
    two_years_back = today - datetime.timedelta(days=730)
    three_years_back = today - datetime.timedelta(days=1095)
    four_years_back = today - datetime.timedelta(days=1460)
    five_years_back = today - datetime.timedelta(days=1825)
    five_years_data_jsons = [
        requests.get(f'https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{one_year_back}/{today}/?format=json').json(),
        requests.get(
            f'https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{two_years_back}/{one_year_back}/?format=json').json(),
        requests.get(
            f'https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{three_years_back}/{two_years_back}/?format=json').json(),
        requests.get(
            f'https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{four_years_back}/{three_years_back}/?format=json').json(),
        requests.get(
            f'https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{five_years_back}/{four_years_back}/?format=json').json(),
    ]
    total_data = []
    for js in five_years_data_jsons:
        for rate in list(reversed(js['rates'])):
            total_data.append(rate)
    context = {'currency': currency,
               'week': get_rates_in_time(week_back, total_data),
               'month': get_rates_in_time(month_back, total_data),
               'two_months': get_rates_in_time(two_months_back, total_data),
               'three_months': get_rates_in_time(three_months_back, total_data),
               'six_months': get_rates_in_time(six_months_back, total_data),
               'one_year': get_rates_in_time(one_year_back, total_data),
               'two_years': get_rates_in_time(two_years_back, total_data),
               'three_years': get_rates_in_time(three_years_back, total_data),
               'five_years': get_rates_in_time(five_years_back, total_data),
               'currencies': get_all_currencies()
               }
    return render(request, 'exchange_rates/exchange_rates_diagram.html', context)
