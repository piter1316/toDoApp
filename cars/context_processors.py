from datetime import timedelta
from django.utils import timezone
from .models import Car


def car_deadline_notifications(request):
    if not request.user.is_authenticated:
        return {'car_notifications': []}

    today = timezone.localdate()
    notifications = []

    cars = Car.objects.filter(
        user=request.user,
        sold=False
    ).only('id', 'name', 'oc_expiry', 'inspection_expiry')

    for car in cars:
        for label, deadline in (
            ('OC', car.oc_expiry),
            ('Przegląd', car.inspection_expiry),
        ):
            if deadline is None:
                continue

            days_left = (deadline - today).days

            if days_left <= 7:
                notifications.append({
                    'car_id': car.pk,
                    'car_name': car.name,
                    'label': label,
                    'date': deadline,
                    'days_left': days_left,
                    'urgent': days_left <= 3,
                })

    notifications.sort(key=lambda item: item['days_left'])

    return {'car_notifications': notifications}