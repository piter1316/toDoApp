# Generated by Django 2.1.2 on 2020-02-25 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meal',
            name='calories',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
