from django.contrib.auth.models import User
from django.db import models


class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=100)
    make = models.TextField(max_length=100, null=True, blank=True)
    model = models.TextField(max_length=100, null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True, default=None)
    engine = models.TextField(max_length=100, null=True, blank=True)
    power = models.FloatField(null=True, blank=True, default=None)
    mileage = models.PositiveIntegerField(null=True, blank=True, default=None)
    logo = models.FileField(null=True, blank=True, default=None)
    image = models.FileField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name

