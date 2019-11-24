from django.contrib.auth.models import User
from django.db import models


class MealOption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    meal_option = models.TextField(max_length=15)

    def __str__(self):
        return self.meal_option


class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    meal_option = models.ForeignKey(MealOption, on_delete=models.CASCADE)
    name = models.TextField(max_length=100)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    meal_id = models.ForeignKey(Meal, on_delete=models.DO_NOTHING, default=1)
    name = models.TextField(max_length=50)
    shop = models.TextField(max_length=50)
    quantity = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.name


class MealsList(models.Model):
    day = models.TextField(max_length=10)
    meals = models.TextField(max_length=100)

