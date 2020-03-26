# Generated by Django 2.1.2 on 2020-03-14 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0003_auto_20200314_1422'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='unit',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='calories_per_100_gram',
            field=models.PositiveIntegerField(default=0),
        ),
    ]