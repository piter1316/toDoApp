from .utils import get_weather_from_ose
from budget.models import UserSettings  # Upewnij się, że nazwa modelu jest poprawna


def home_weather_processor(request):
    # Jeśli użytkownik nie jest zalogowany, nic nie wyświetlamy
    if not request.user.is_authenticated:
        return {}

    try:
        # Pobieramy ustawienia zalogowanego użytkownika
        settings = UserSettings.objects.get(user=request.user)

        if settings.home_station_id:
            # Używamy Twojej funkcji helpera z utils.py
            weather_data = get_weather_from_ose(settings.home_station_id)
            return {
                'navbar_weather': weather_data
            }
    except UserSettings.DoesNotExist:
        pass

    return {}