import math

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, F, FloatField
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

VEGIES_OUT = ('ziemniaki', 'passata pomidorowa', 'tofu', 'przecier pomidorowy')


def is_hi_protein(total_kcal, total_protein):
    if total_protein != 0 or total_kcal != 0:
        percent_of_prot = round((total_protein * 4) / total_kcal * 100, 2)
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

    # --- NOWE POLA DO OPTYMALIZACJI ---
    total_kcal = models.FloatField(default=0)
    total_protein = models.FloatField(default=0)
    total_fat = models.FloatField(default=0)
    total_carb = models.FloatField(default=0)
    total_vegies = models.FloatField(default=0)
    total_fruits = models.FloatField(default=0)
    is_hi_protein_flag = models.CharField(max_length=2, null=True, blank=True)  # Zapisze 'B' lub 'b'
    has_short_expiry_flag = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def has_short_expiry(self):
        meal_ingredients = MealIngredient.objects.filter(meal_id=self.id)
        short_expiry_check = [ingr.ingredient_id.short_expiry for ingr in meal_ingredients]
        return True in short_expiry_check

    @property
    def macro(self):
        meals_prep = MealIngredient.objects.filter(meal_id=self.id).select_related('ingredient_id')
        meal_ingredients = (
            meals_prep.annotate(
                kcal=F('ingredient_id__calories_per_100_gram') * F('quantity') / 100,
                protein=F('ingredient_id__protein_per_100_gram') * F('quantity') / 100,
                fat=F('ingredient_id__fat_per_100_gram') * F('quantity') / 100,
                carb=F('ingredient_id__carbohydrates_per_100_gram') * F('quantity') / 100,

            )
        )
        total_vegies = 0
        total_fruits = 0
        for m in meals_prep:
            if ('warzywa' in m.ingredient_id.division.division_name.lower() and
                    m.ingredient_id.name.lower() not in VEGIES_OUT):
                total_vegies += m.quantity
            if 'owoce' in m.ingredient_id.division.division_name.lower():
                total_fruits += m.quantity

        total_kcal = meal_ingredients.aggregate(total_kcal=Sum('kcal', output_field=FloatField()))['total_kcal'] or 0
        total_protein = meal_ingredients.aggregate(total_protein=Sum('protein', output_field=FloatField()))[
                            'total_protein'] or 0
        total_fat = meal_ingredients.aggregate(total_fat=Sum('fat', output_field=FloatField()))[
                        'total_fat'] or 0
        total_carbohydrates = meal_ingredients.aggregate(total_carbohydrates=Sum('carb', output_field=FloatField()))[
                                  'total_carbohydrates'] or 0

        return {'kcal': total_kcal, 'protein': total_protein, 'fat': total_fat, 'carb': total_carbohydrates,
                'is_hi_protein': is_hi_protein(total_kcal, total_protein), 'total_vegies': total_vegies,
                'total_fruits': total_fruits}


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

    @property
    def meals_with_ingredient(self):
        return MealIngredient.objects.filter(ingredient_id=self.pk).select_related('meal_id')


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


# Upewnij się, że ten kod znajduje się pod definicjami klas Meal i MealIngredient
# oraz że masz zaimportowaną zmienną VEGIES_OUT i funkcję is_hi_protein.

def update_meal_stats_on_change(sender, instance, **kwargs):
    meal = instance.meal_id  # U Ciebie ForeignKey nazywa się meal_id
    if not meal:
        return

    # Pobieramy wszystkie składniki posiłku
    ingredients = MealIngredient.objects.filter(meal_id=meal).select_related('ingredient_id__division')

    t_kcal = t_prot = t_fat = t_carb = t_veg = t_fru = 0.0
    has_short = False

    for mi in ingredients:
        ing = mi.ingredient_id
        q = float(mi.quantity)
        factor = q / 100.0

        t_kcal += ing.calories_per_100_gram * factor
        t_prot += ing.protein_per_100_gram * factor
        t_fat += ing.fat_per_100_gram * factor
        t_carb += ing.carbohydrates_per_100_gram * factor

        if ing.short_expiry:
            has_short = True

        div_name = ing.division.division_name.lower()
        if 'warzywa' in div_name and ing.name.lower() not in VEGIES_OUT:
            t_veg += q
        if 'owoce' in div_name:
            t_fru += q

    # Zapisujemy przeliczone dane do obiektu Meal
    meal.total_kcal = round(t_kcal)
    meal.total_protein = round(t_prot)
    meal.total_fat = round(t_fat)
    meal.total_carb = round(t_carb)
    meal.total_vegies = round(t_veg)
    meal.total_fruits = round(t_fru)
    meal.has_short_expiry_flag = has_short

    # Obsługa flagi białka
    res = is_hi_protein(t_kcal, t_prot)
    meal.is_hi_protein_flag = res[0] if res else None

    # Ważne: używamy update_fields, aby nie triggerować innych sygnałów w kółko
    meal.save(update_fields=[
        'total_kcal', 'total_protein', 'total_fat', 'total_carb',
        'total_vegies', 'total_fruits', 'has_short_expiry_flag', 'is_hi_protein_flag'
    ])


post_save.connect(update_meal_stats_on_change, sender=MealIngredient)
post_delete.connect(update_meal_stats_on_change, sender=MealIngredient)
