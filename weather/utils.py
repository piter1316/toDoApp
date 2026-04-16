import requests
from django.core.cache import cache


def get_nask_weather(station_id):
    if not station_id:
        return None

    # Tworzymy unikalny klucz dla danej stacji w cache
    cache_key = f'nask_weather_{station_id}'
    cached_data = cache.get(cache_key)

    # Jeśli mamy świeże dane w pamięci, od razu je zwracamy
    if cached_data:
        return cached_data

    url = f"https://esa.nask.pl/api/data/id/{station_id}"
    try:
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiJkNTc4MWUxMS0yZmJkLTQyYTMtYWYzYS05MjU0MzYzMDcxODAiLCJpc3MiOiJFU0EiLCJzdWIiOiJlc2EubmFzay5wbCIsImlhdCI6MTc3NjMxOTM3MywiZXhwIjoxNzc2NDkyMTczLCJBdXRob3JpdGllcyI6WyJTTU9HX1BBR0UiXX0.Sa5q3v0ZvQybm54eYvLa4Ug7nv3NFwgjQd51P2V8OY-UU4cUxNbIOY2mZK8DzMPQOJcdhqOsS9QrqkZhpQL4-w'}

        # Ustawiamy krótki timeout, żeby apka nie "wisiała" jak serwery NASK padną
        response = requests.get(url, timeout=3, headers=headers)
        if response.status_code == 200:
            data = response.json()
            sensors = data.get('sensors', [])

            outside_data = None
            # Szukamy czujnika zewnętrznego
            for sensor in sensors:
                if sensor.get('placement') == 'OUTSIDE':
                    outside_data = sensor.get('lastMeasurement')
                    break

            if outside_data:
                # Formatujemy kolory hex dodając # na początek (jeśli istnieje)
                pm25_color = outside_data.get('pm25', {}).get('color')
                pm25_color = f"#{pm25_color}" if pm25_color else "#999999"

                result = {
                    'temp': outside_data.get('temperature'),
                    'hum': outside_data.get('humidity'),
                    'press': outside_data.get('pressure'),
                    'pm25': outside_data.get('pm25', {}).get('value'),
                    'pm25_color': pm25_color,
                    'pm10': outside_data.get('pm10', {}).get('value'),
                }

                # Zapisujemy w Cache na 15 minut (900 sekund)
                cache.set(cache_key, result, 900)
                return result
    except requests.RequestException:
        pass  # Jeśli API leży, ignorujemy błąd (zwróci None)

    return None