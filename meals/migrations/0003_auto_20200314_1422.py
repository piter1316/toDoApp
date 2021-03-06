# Generated by Django 2.1.2 on 2020-03-14 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0002_meal_calories'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='meal_id',
        ),
        migrations.AddField(
            model_name='mealingredient',
            name='ingredient_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meals.Ingredient'),
        ),
        migrations.AddField(
            model_name='mealingredient',
            name='meal_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meals.Meal'),
        ),
    ]
