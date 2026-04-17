import requests
import sys

# Konfiguracja
SOURCE_URL = "https://public-esa.ose.gov.pl/api/v1/smog"
DEST_URL = "https://piter1316.pythonanywhere.com/weather/update-weather/"
# DEST_URL = "http://127.0.0.1:8000/weather/update-weather/"
SECRET_KEY = "TwojeTajneHaslo123"  # Wymyśl własne


def relay():
    try:
        # 1. Pobierz z OSE
        response = requests.get(SOURCE_URL, timeout=30)
        response.raise_for_status()
        data = response.json()

        # 2. Wyślij do Django
        headers = {'X-Relay-Auth': SECRET_KEY}
        post_res = requests.post(DEST_URL, json=data, headers=headers, timeout=60)

        if post_res.status_code == 200:
            print("Sukces: Dane przesłane.")
        else:
            print(f"Błąd Django: {post_res.status_code}")

    except Exception as e:
        raise
        print(f"Błąd: {e}")
        sys.exit(1)


if __name__ == "__main__":
    relay()
