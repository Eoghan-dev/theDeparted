from django.db import models
import requests
from datetime import datetime

class CurrentWeather(models.Model):
    """
    Stores current weather information,
    data for this model will be harvested from the openweather api
    """
    entry_id = models.AutoField(primary_key=True) # Auto increment primary key
    timestamp = models.BigIntegerField() # Timestamp of when the API call was made
    dt = models.DateTimeField()
    weather_id = models.IntegerField()
    weather_main = models.CharField(max_length=256)
    coord_lon = models.FloatField()
    coord_lat = models.FloatField()
    weather_description = models.CharField(max_length=500)
    weather_icon = models.CharField(max_length=256)
    weather_icon_url = models.CharField(max_length=256)
    base = models.CharField(max_length=256)
    main_temp = models.FloatField()
    main_feels_like = models.FloatField()
    main_temp_min = models.FloatField()
    main_temp_max = models.FloatField()
    main_pressure = models.IntegerField()
    main_humidity = models.IntegerField()
    visibility = models.IntegerField()
    wind_speed = models.FloatField()
    wind_deg = models.IntegerField()
    clouds_all = models.IntegerField()
    sys_type = models.IntegerField()
    sys_id = models.IntegerField()
    sys_country = models.CharField(max_length=256)
    sys_sunrise = models.BigIntegerField()
    sys_sunset = models.BigIntegerField()
    timezone = models.BigIntegerField()
    id = models.BigIntegerField()
    name = models.CharField(max_length=256)
    cod = models.IntegerField()

    def __str__(self):
        """String representation of the model, can be changed to anything"""
        str_output = f"\n*****\n" \
                     f"Entry id:{self.entry_id}\n" \
                     f"Weather description:{self.weather_description}\n" \
                     f"Datetime:{self.dt}\n" \
                     f"*****\n"
        return str_output

    @classmethod
    def scrape(cls):
        """
        Method to make a call to the open weather for a hard coded set of co-ordinates and save the info in our db
        """
        # Make the api request and parse it as json
        latitude = '53.349805'
        longitude = '-6.26031'
        weather_key = "7ac118753938be7d1540e9f996c5aab4"
        weather_by_coordinates = 'http://api.openweathermap.org/data/2.5/weather'
        r = requests.get(weather_by_coordinates, params={"APPID": weather_key, "lat": latitude, "lon": longitude})
        weather_json = r.json()

        # Make an object for the current update that is being scraped
        latestUpdate = CurrentWeather(
            timestamp=int(weather_json['dt']),
            dt=datetime.fromtimestamp(int(weather_json['dt'])),
            coord_lon=longitude,
            coord_lat=latitude,

            weather_id=weather_json['weather'][0]['id'],
            weather_main=weather_json['weather'][0]['main'],
            weather_description = weather_json['weather'][0]['description'],
            weather_icon = weather_json['weather'][0]['icon'],
            weather_icon_url = 'http://openweathermap.org/img/wn/{}@2x.png'.format(weather_json['weather'][0]['icon']),

            base = weather_json['base'],
            main_temp = weather_json['main']['temp'],
            main_feels_like = weather_json['main']['feels_like'],
            main_temp_min = weather_json['main']['temp_min'],
            main_temp_max = weather_json['main']['temp_max'],
            main_pressure = weather_json['main']['pressure'],
            main_humidity = weather_json['main']['humidity'],
            visibility = weather_json['visibility'],

            wind_speed = weather_json['wind']['speed'],
            wind_deg = weather_json['wind']['deg'],

            clouds_all = weather_json['clouds']['all'],

            sys_type = weather_json['sys']['type'],
            sys_id = weather_json['sys']['id'],
            sys_country = weather_json['sys']['country'],
            sys_sunrise = weather_json['sys']['sunrise'],
            sys_sunset = weather_json['sys']['sunset'],

            timezone = weather_json['timezone'],
            id = weather_json['id'],
            name = weather_json['name'],
            cod = weather_json['cod'],
        )
        # Store the object which represents a row in our table into the database table
        latestUpdate.save()