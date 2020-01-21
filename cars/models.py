from django.contrib.auth.models import User
from django.db import models


class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=100)
    make = models.TextField(max_length=100, null=True, blank=True)
    model = models.TextField(max_length=100, null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    engine = models.TextField(max_length=100, null=True, blank=True)
    power = models.FloatField(null=True, blank=True)
    milage = models.PositiveIntegerField(null=True, blank=True)
    logo = models.FileField(null=True, blank=True)
    image = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.name
