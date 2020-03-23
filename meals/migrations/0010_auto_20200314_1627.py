# Generated by Django 2.1.2 on 2020-03-14 15:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0009_shop_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='weight_per_unit',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
    ]
