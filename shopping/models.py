from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from meals.models import Unit


class ShoppingList(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=100)

    def __str__(self):
        return self.name


class Products(models.Model):
    shopping_list_id = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    product_name = models.TextField(max_length=150)
    quantity = models.SmallIntegerField(default=1)
    unit = models.ForeignKey(Unit, default=1, on_delete=models.DO_NOTHING)
    bought = models.BooleanField(default=False)

    def __str__(self):
        return self.product_name

