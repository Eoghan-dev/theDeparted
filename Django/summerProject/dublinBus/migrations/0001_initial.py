# Generated by Django 3.2.4 on 2021-06-21 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CurrentWeather',
            fields=[
                ('entry_id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.BigIntegerField()),
                ('dt', models.DateTimeField()),
                ('weather_id', models.IntegerField()),
                ('weather_main', models.CharField(max_length=256)),
                ('coord_lon', models.FloatField()),
                ('coord_lat', models.FloatField()),
                ('weather_description', models.CharField(max_length=500)),
                ('weather_icon', models.CharField(max_length=256)),
                ('weather_icon_url', models.CharField(max_length=256)),
                ('base', models.CharField(max_length=256)),
                ('main_temp', models.FloatField()),
                ('main_feels_like', models.FloatField()),
                ('main_temp_min', models.FloatField()),
                ('main_temp_max', models.FloatField()),
                ('main_pressure', models.IntegerField()),
                ('main_humidity', models.IntegerField()),
                ('visibility', models.IntegerField()),
                ('wind_speed', models.FloatField()),
                ('wind_deg', models.IntegerField()),
                ('clouds_all', models.IntegerField()),
                ('sys_type', models.IntegerField()),
                ('sys_id', models.IntegerField()),
                ('sys_country', models.CharField(max_length=256)),
                ('sys_sunrise', models.BigIntegerField()),
                ('sys_sunset', models.BigIntegerField()),
                ('timezone', models.BigIntegerField()),
                ('id', models.BigIntegerField()),
                ('name', models.CharField(max_length=256)),
                ('cod', models.IntegerField()),
            ],
        ),
    ]
