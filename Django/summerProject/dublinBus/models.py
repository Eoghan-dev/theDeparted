from django.db import models
# Import our functions used in our scrape methods for certain models
from . import scrapers

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
        # Make api call to get the results in a json file
        weather_json = scrapers.get_current_weather()
        # Create a CurrentWeather object with this json file and write it to the db
        scrapers.write_current_weather(weather_json)
        print("Finished scraping CurrentWeather!")


class CurrentBus(models.Model):
    """
    Stores current bus information,
    data for this model will be harvested from gtfs transport for ireland
    """
    timestamp = models.BigIntegerField() # timestamp of when the api call was made
    dt = models.DateTimeField() # datetime representation of the above timestamp
    trip_id = models.CharField(max_length=256)
    route_id = models.CharField(max_length=256)
    schedule = models.CharField(max_length=256)
    start_t = models.CharField(max_length=256)
    start_d = models.CharField(max_length=256)
    stop_id = models.CharField(max_length=256)
    delay = models.IntegerField()

    def __str__(self):
        """String representation of the model, can be changed to anything"""
        str_output = f"*****" \
                     f"id: {self.id}" \
                     f"datetime: {self.dt}" \
                     f"delay: {self.delay}"
        return str_output

    @classmethod
    def scrape(cls):
        # Make api call to gtfs transport for Ireland api and store the result as json in a variable
        transport_data = scrapers.get_current_bus()
        # Pass this json data through to our functiont that creates a CurrentBus object and writes it to the db
        scrapers.write_current_bus(transport_data)
        print("Finished scraping CurrentBus!")