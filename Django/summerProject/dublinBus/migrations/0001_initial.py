# Generated by Django 3.0 on 2021-08-06 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusStops',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_id', models.CharField(max_length=256)),
                ('stop_name', models.CharField(max_length=256)),
                ('stop_number', models.CharField(max_length=256)),
                ('stop_lat', models.FloatField()),
                ('stop_lon', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Current_timetable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.BigIntegerField()),
                ('dt', models.DateTimeField()),
                ('route', models.CharField(max_length=8)),
                ('direction', models.CharField(max_length=32)),
                ('day', models.CharField(max_length=8)),
                ('leave_t', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='CurrentBus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.BigIntegerField()),
                ('dt', models.DateTimeField()),
                ('trip_id', models.CharField(max_length=256)),
                ('direction', models.CharField(max_length=2)),
                ('route_id', models.CharField(max_length=256)),
                ('route', models.CharField(max_length=6)),
                ('schedule', models.CharField(max_length=256)),
                ('start_t', models.CharField(max_length=256)),
                ('start_d', models.CharField(max_length=256)),
                ('stop_id', models.CharField(max_length=256, null=True)),
                ('delay', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CurrentWeather',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.BigIntegerField()),
                ('dt', models.DateTimeField()),
                ('weather_main', models.CharField(max_length=256)),
                ('weather_description', models.CharField(max_length=500)),
                ('weather_icon', models.CharField(max_length=256)),
                ('weather_icon_url', models.CharField(max_length=256)),
                ('main_temp', models.FloatField()),
                ('weather_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='WeatherForecast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.BigIntegerField()),
                ('dt', models.DateTimeField()),
                ('weather_main', models.CharField(max_length=256)),
                ('weather_description', models.CharField(max_length=500)),
                ('weather_icon', models.CharField(max_length=256)),
                ('weather_icon_url', models.CharField(max_length=256)),
                ('main_temp', models.FloatField()),
                ('weather_id', models.IntegerField()),
            ],
        ),
    ]
