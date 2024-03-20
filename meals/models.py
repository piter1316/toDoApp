import math

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, F, FloatField, Case, When, Value


def is_hi_protein(total_kcal, total_protein):
    if total_protein != 0 or total_kcal != 0:
        percent_of_prot = round((total_protein * 4)/total_kcal * 100, 2)
        if total_protein * 4 >= (total_kcal * 0.28):
            return 'B', f'Bardzo wysoka zawartość białka ({percent_of_prot}%)'
        if (total_kcal * 0.25) <= total_protein * 4 < (total_kcal * 0.28):
            return 'b', f'wysoka zawartość białka ({percent_of_prot}%)'


class MealOption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    meal_option = models.TextField(max_length=15)
    position = models.SmallIntegerField(default=0)
    is_taken_to_generation = models.IntegerField(blank=True, null=True, default=1)

    def __str__(self):
        return self.meal_option


class Meal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    meal_option = models.ForeignKey(MealOption, on_delete=models.CASCADE)
    name = models.TextField(max_length=100)
    recipe = models.TextField(null=True, blank=True)
    special = models.BooleanField(default=False)
    calories = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def has_short_expiry(self):
        meal_ingredients = MealIngredient.objects.filter(meal_id=self.id)
        short_expiry_check = [ingr.ingredient_id.short_expiry for ingr in meal_ingredients]
        return True in short_expiry_check

    @property
    def is_high_carb(self):
        meal_ingredients = (
            MealIngredient.objects
            .filter(meal_id=self.id)
            .select_related('ingredient_id')
            .annotate(
                kcal=F('ingredient_id__calories_per_100_gram') * F('quantity') / 100,
                protein=F('ingredient_id__protein_per_100_gram') * F('quantity') / 100
            )
        )
        total_kcal = meal_ingredients.aggregate(total_kcal=Sum('kcal', output_field=FloatField()))['total_kcal'] or 0
        total_protein = meal_ingredients.aggregate(total_protein=Sum('protein', output_field=FloatField()))[
                            'total_protein'] or 0

        return is_hi_protein(total_kcal, total_protein)


class ProductDivision(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    division_name = models.TextField(max_length=100, default=1)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return self.division_name


class Shop(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.TextField(max_length=100)

    def __str__(self):
        return self.name


class Unit(models.Model):
    unit = models.TextField(max_length=5)

    def __str__(self):
        return self.unit


class Ingredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, default=1)
    name = models.TextField(max_length=50)
    calories_per_100_gram = models.PositiveIntegerField(default=0)
    protein_per_100_gram = models.PositiveIntegerField(default=0)
    fat_per_100_gram = models.PositiveIntegerField(default=0)
    carbohydrates_per_100_gram = models.PositiveIntegerField(default=0)
    weight_per_unit = models.PositiveIntegerField(default=0)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, default=1, null=True)
    short_expiry = models.BooleanField(default=False, null=True)
    division = models.ForeignKey(ProductDivision, models.DO_NOTHING, default=1)

    def __str__(self):
        return self.name


class MealIngredient(models.Model):
    meal_id = models.ForeignKey(Meal, on_delete=models.CASCADE)
    ingredient_id = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(default=1)

    def __str__(self):
        return self.ingredient_id.name

    @property
    def kcal(self):
        return math.ceil(self.ingredient_id.calories_per_100_gram * self.quantity / 100)

    @property
    def protein(self):
        return math.ceil(self.ingredient_id.protein_per_100_gram * self.quantity / 100)

    @property
    def fat(self):
        return math.ceil(self.ingredient_id.fat_per_100_gram * self.quantity / 100)

    @property
    def carb(self):
        return math.ceil(self.ingredient_id.carbohydrates_per_100_gram * self.quantity / 100)


class MealsList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    day = models.TextField(max_length=10)
    meal_option = models.ForeignKey(MealOption, on_delete=models.DO_NOTHING, default=1)
    meal = models.ForeignKey(Meal, on_delete=models.DO_NOTHING, db_column='meal_id', default=1, null=True, blank=True)
    current = models.BooleanField(default=False)
    extras = models.ForeignKey(Meal, models.DO_NOTHING, db_column='extras', related_name='%(class)s_meals_meal',
                               blank=True, null=True)

    def __str__(self):
        if self.meal:
            return self.meal.name
        else:
            return ''

    def day_as_list(self):
        return self.day.split('_')


class Week(models.Model):
    day_of_the_week = models.TextField(max_length=15)

    def __str__(self):
        return self.day_of_the_week
