from django.contrib.auth.models import User
from django.db import models


# Create your models here.
from meals.models import Unit, Shop, ProductDivision


class ShoppingList(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=100)
    generated = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Products(models.Model):
    shopping_list_id = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    product_name = models.TextField(max_length=150)
    quantity = models.FloatField(default=1)
    unit = models.ForeignKey(Unit, default=1, on_delete=models.DO_NOTHING)
    bought = models.BooleanField(default=False)
    division_id = models.ForeignKey(ProductDivision, on_delete=models.DO_NOTHING, default=None)

    def __str__(self):
        return self.product_name


class Checklist(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    shop = models.ForeignKey(Shop, models.DO_NOTHING, blank=True, null=True)
    product_name = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.product_name

    class Meta:
        managed = False
        db_table = 'shopping_checklist'


