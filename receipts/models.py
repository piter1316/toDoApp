import datetime

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.TextField(max_length=200)
    icon = models.TextField(max_length=200)

    def __str__(self):
        return self.name


class Receipt(models.Model):
    name = models.TextField(max_length=200)
    purchase_date = models.DateField(null=False, blank=False)
    warranty = models.PositiveIntegerField(null=True, blank=True, default=None)
    price = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=12)
    shop = models.TextField(max_length=200, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, default=12)
    notes = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def warranty_left(self):
        if self.warranty:
            warranty_date = self.purchase_date + datetime.timedelta(days=self.warranty)
            return (warranty_date - datetime.date.today()).days
        else:return 0

