# Generated by Django 2.1.2 on 2020-02-26 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0005_auto_20200220_1217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='labour',
        ),
        migrations.AddField(
            model_name='sparepart',
            name='service',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]