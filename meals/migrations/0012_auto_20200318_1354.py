# Generated by Django 2.1.2 on 2020-03-18 12:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0011_auto_20200316_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='shop',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='meals.Shop'),
        ),
    ]
