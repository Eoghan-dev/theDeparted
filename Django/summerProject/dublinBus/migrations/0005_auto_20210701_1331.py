# Generated by Django 3.0 on 2021-07-01 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dublinBus', '0004_bus_stops'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus_stops',
            name='stop_lat',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='bus_stops',
            name='stop_lon',
            field=models.FloatField(),
        ),
    ]