import hashlib

import requests
from django.core.cache import cache


# def get_nask_weather(station_id):
#     if not station_id:
#         return None
#
#     # Tworzymy unikalny klucz dla danej stacji w cache
#     cache_key = f'nask_weather_{station_id}'
#     cached_data = cache.get(cache_key)
#
#     # Jeśli mamy świeże dane w pamięci, od razu je zwracamy
#     if cached_data:
#         return cached_data
#
#     url = f"https://esa.nask.pl/api/data/id/{station_id}"
#     try:
#         headers = {
#             'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiJkNTc4MWUxMS0yZmJkLTQyYTMtYWYzYS05MjU0MzYzMDcxODAiLCJpc3MiOiJFU0EiLCJzdWIiOiJlc2EubmFzay5wbCIsImlhdCI6MTc3NjMxOTM3MywiZXhwIjoxNzc2NDkyMTczLCJBdXRob3JpdGllcyI6WyJTTU9HX1BBR0UiXX0.Sa5q3v0ZvQybm54eYvLa4Ug7nv3NFwgjQd51P2V8OY-UU4cUxNbIOY2mZK8DzMPQOJcdhqOsS9QrqkZhpQL4-w'}
#
#         # Ustawiamy krótki timeout, żeby apka nie "wisiała" jak serwery NASK padną
#         response = requests.get(url, timeout=3, headers=headers)
#         if response.status_code == 200:
#             data = response.json()
#             sensors = data.get('sensors', [])
#
#             outside_data = None
#             # Szukamy czujnika zewnętrznego
#             for sensor in sensors:
#                 if sensor.get('placement') == 'OUTSIDE':
#                     outside_data = sensor.get('lastMeasurement')
#                     break
#
#             if outside_data:
#                 # Formatujemy kolory hex dodając # na początek (jeśli istnieje)
#                 pm25_color = outside_data.get('pm25', {}).get('color')
#                 pm25_color = f"#{pm25_color}" if pm25_color else "#999999"
#
#                 result = {
#                     'temp': outside_data.get('temperature'),
#                     'hum': outside_data.get('humidity'),
#                     'press': outside_data.get('pressure'),
#                     'pm25': outside_data.get('pm25', {}).get('value'),
#                     'pm25_color': pm25_color,
#                     'pm10': outside_data.get('pm10', {}).get('value'),
#                 }
#
#                 # Zapisujemy w Cache na 15 minut (900 sekund)
#                 cache.set(cache_key, result, 900)
#                 return result
#     except requests.RequestException:
#         pass  # Jeśli API leży, ignorujemy błąd (zwróci None)
#
#     return None
def get_all_ose_data():

    cache_key = 'ose_all_stations_data'
    all_data = cache.get(cache_key)

    if all_data:
        return all_data

    url = "https://public-esa.ose.gov.pl/api/v1/smog"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            json_data = response.json()
            all_data = json_data.get('smog_data', [])

            cache.set(cache_key, all_data, 650)
            return all_data

    except Exception as e:
        print(f"Błąd pobierania całej bazy OSE: {e}")
        return []


def get_weather_from_ose(target_school_name):
    all_stations = get_all_ose_data()

    if not all_stations:
        return None

    station = next((
        s for s in all_stations
        if s.get('school', {}).get('name', '').strip().upper() == target_school_name.strip().upper()
    ), None)

    if station:
        measurements = station.get('data', {})
        return {
            'temp': measurements.get('temperature_avg'),
            'hum': measurements.get('humidity_avg'),
            'press': measurements.get('pressure_avg'),
            'pm25': measurements.get('pm25_avg'),
            'pm10': measurements.get('pm10_avg'),
            'timestamp': station.get('timestamp'),
            'source': 'OSE/NASK'
        }

    return None
