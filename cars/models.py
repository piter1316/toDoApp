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
    sold = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        return self.name


class Fuel(models.Model):
    car_id = models.ForeignKey(Car, on_delete=models.DO_NOTHING)
    date = models.DateField(null=False, blank=False)
    liters = models.FloatField(null=False, blank=False)
    kilometers = models.FloatField(null=False, blank=False)
    fuel_price = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=4)
    mileage = models.PositiveIntegerField(null=True, blank=True, default=None)


class Service(models.Model):
    car_id = models.ForeignKey(Car, on_delete=models.DO_NOTHING)
    date = models.DateField(null=False, blank=False)
    mileage = models.PositiveIntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return str(self.date) + ' ' + str(self.mileage)


class SparePart(models.Model):
    service_id = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
    name = models.TextField(max_length=160)
    price = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=10)
    service = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    service_id = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
    name = models.TextField(max_length=160)
    file = models.FileField(null=True, blank=True, default=None)

    def __str__(self):
        return self.name