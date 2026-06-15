import requests
from django.core.cache import cache


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

            cache.set(cache_key, all_data, 300)
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
