import json
import os

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from budget.models import UserSettings  # Zakładam taką nazwę modelu
from weather.utils import get_nask_weather


# Funkcja pomocnicza do ładowania stacji
def load_stations():
    path = os.path.join(os.path.dirname(__file__), 'stations.json')
    with open(path, 'r', encoding='utf-8') as f:
        full_data = json.load(f)['data']

        # Filtrujemy: zostawiamy tylko te, które mają obiekt 'outside'
        # i których 'pm10' nie jest nullem
        filtered_stations = [
            s for s in full_data
            if s.get('outside') and s['outside'].get('pm10') is not None
        ]

        return filtered_stations


@login_required
def weather_dashboard(request):
    stations = load_stations()
    user_settings, created = UserSettings.objects.get_or_create(user=request.user)

    # Przekształcamy string "1,2,3" w listę intów
    raw_stations = user_settings.weather_stations or ""
    selected_ids = [int(i) for i in raw_stations.split(',') if i]

    if request.method == "POST":
        action = request.POST.get('action')
        station_id = request.POST.get('station_id')

        if action == "add" and station_id:
            if int(station_id) not in selected_ids:
                selected_ids.append(int(station_id))
        elif action == "remove":
            selected_ids.remove(int(station_id))
            if user_settings.home_station_id == int(station_id):
                user_settings.home_station_id = None
        elif action == "set_home":
            user_settings.home_station_id = int(station_id)

        user_settings.weather_stations = ",".join(map(str, selected_ids))
        user_settings.save()

        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            # Ponownie pobieramy i sortujemy stacje po zmianach
            user_stations = [s for s in stations if s['id'] in selected_ids]
            home_weather_data = get_nask_weather(user_settings.home_station_id)
            for station in user_stations:
                station['live_data'] = get_nask_weather(station['id'])
            user_stations.sort(key=lambda x: x['id'] == user_settings.home_station_id, reverse=True)

            html = render_to_string('weather/weather_grid.html', {
                'user_stations': user_stations,
                'home_id': user_settings.home_station_id,
                'csrf_token': request.META.get('CSRF_COOKIE')  # Ważne dla formularzy
            }, request=request)
            # Renderujemy fragment navbara (NOWOŚĆ)
            navbar_html = render_to_string('weather/navbar_weather.html', {
                'navbar_weather': home_weather_data
            }, request=request)
            return JsonResponse({'html': html, 'navbar_html': navbar_html})
        return redirect('weather:weather_dashboard')

    # Pobieramy pełne obiekty stacji, które wybrał użytkownik
    user_stations = [s for s in stations if s['id'] in selected_ids]
    for station in user_stations:
        station['live_data'] = get_nask_weather(station['id'])
    user_stations.sort(key=lambda x: x['id'] == user_settings.home_station_id, reverse=True)

    return render(request, 'weather/weather_dash.html', {
        'user_stations': user_stations,
        'home_id': user_settings.home_station_id,
        'all_stations_json': json.dumps(stations)  # Do podpowiedzi w JS
    })


def home_weather(request):
    if not request.user.is_authenticated:
        return {}

    settings = getattr(request.user, 'budget_usersettings', None)
    if settings and settings.home_station_id:
        # Tutaj możesz pobrać dane z API NASK na podstawie ID
        # Na razie zwrócimy tylko ID do paska menu
        return {'navbar_home_station_id': settings.home_station_id}
    return {}
# def weather_dashboard(request):
#     context = {}
#     return render(request, 'weather/weather_dash.html', context)
