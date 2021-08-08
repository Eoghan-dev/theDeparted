from django.db import models
# Import our functions used in our scrape methods for certain models
from . import scrapers

class CurrentWeather(models.Model):
    """
    Stores current weather information,
    data for this model will be harvested from the openweather api
    """
    timestamp = models.BigIntegerField() # Timestamp of when the API call was made
    dt = models.DateTimeField()
    weather_main = models.CharField(max_length=256)
    weather_description = models.CharField(max_length=500)
    weather_icon = models.CharField(max_length=256)
    weather_icon_url = models.CharField(max_length=256)
    main_temp = models.FloatField()
    weather_id = models.IntegerField()

    def __str__(self):
        """String representation of the model, can be changed to anything"""
        str_output = f"\n*****\n" \
                     f"Entry id:{self.entry_id}\n" \
                     f"Weather description:{self.weather_description}\n" \
                     f"Datetime:{self.dt}\n" \
                     f"*****\n"
        return str_output

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

class WeatherForecast(models.Model):
    """Stores current weather information,
    data for this model will be harvested from the openweather api 3 hour forecast for 5 days
    """
    timestamp = models.BigIntegerField() # Timestamp of when the API call was made
    dt = models.DateTimeField()
    weather_main = models.CharField(max_length=256)
    weather_description = models.CharField(max_length=500)
    weather_icon = models.CharField(max_length=256)
    weather_icon_url = models.CharField(max_length=256)
    main_temp = models.FloatField()
    weather_id = models.IntegerField()

    @classmethod
    def scrape(cls):
        """
        Method to make a call to the open weather for a hard coded set of co-ordinates and save the info in our db
        """
        # Make api call to get the results in a json file
        weather_json = scrapers.get_weather_forecast()
        # Create a CurrentWeather object with this json file and write it to the db
        scrapers.write_weather_forecast(weather_json)
        print("Finished scraping CurrentWeather!")

class CurrentBus(models.Model):
    """
    Stores current bus information,
    data for this model will be harvested from gtfs transport for ireland
    """
    timestamp = models.BigIntegerField() # timestamp of when the api call was made
    dt = models.DateTimeField() # datetime representation of the above timestamp
    trip_id = models.CharField(max_length=256)
    direction = models.CharField(max_length=2)
    route_id = models.CharField(max_length=256)
    route = models.CharField(max_length=6)
    schedule = models.CharField(max_length=256)
    start_t = models.CharField(max_length=256)
    start_d = models.CharField(max_length=256)
    stop_id = models.CharField(max_length=256, null=True)
    delay = models.IntegerField(null=True)

    def __str__(self):
        """String representation of the model, can be changed to anything"""
        str_output = f"*****" \
                     f"id: {self.id}" \
                     f"datetime: {self.dt}" \
                     f"delay: {self.delay}" \
                     f"*****"
        return str_output

    @classmethod
    def scrape(cls):
        # Make api call to gtfs transport for Ireland api and store the result as json in a variable
        transport_data = scrapers.get_current_bus()
        # Pass this json data through to our functiont that creates a CurrentBus object and writes it to the db
        scrapers.write_current_bus(transport_data)
        print("Finished scraping CurrentBus!")

class BusStops(models.Model):
    """
    Stores current bus stop information,
    data for this model will be harvested from gtfs transport for ireland
    """
    stop_id = models.CharField(max_length=256)
    stop_name = models.CharField(max_length=256)
    stop_number = models.CharField(max_length=256)
    stop_lat = models.FloatField()
    stop_lon = models.FloatField()

    def __str__(self):
        """String representation of the model, can be changed to anything"""
        str_output = f"*****" \
                     f"id: {self.stop_id}" \
                     f"name: {self.stop_name}" \
                     f"stop_number: {self.stop_number}" \
                     f"stop_lat: {self.stop_lat}"\
                     f"stop_lon: {self.stop_lon}" \
                     f"*****"
        return str_output

    @classmethod
    def scrape(cls):
        scrapers.get_bus_stop()
        print("Finished scraping Bus stops!")

class Current_timetable(models.Model):
    """
    Stores current bus timetable,
    data for this model will be harvested from gtfs transport for ireland
    """
    timestamp = models.BigIntegerField() # timestamp of when the api call was made
    dt = models.DateTimeField() # datetime representation of the above timestamp
    route = models.CharField(max_length=8)
    direction = models.CharField(max_length=32)
    day = models.CharField(max_length=8)
    leave_t = models.CharField(max_length=32)

    def __str__(self):
        """String representation of the model, can be changed to anything"""
        str_output = f"*****" \
                     f"Route: {self.route}" \
                     f"Direction: {self.direction}" \
                     f"Day: {self.day}" \
                     f"Leave_time: {self.leave_t}" \
                     f"*****"
        return str_output

    @classmethod
    def scrape(cls):
        # Make api call to gtfs transport for Ireland api and store the result as json in a variable
        scrapers.get_bus_timetable()
        print("Finished scraping Dublin_bus_timetable!")

class Current_timetable_all(models.Model):


    route = models.CharField(max_length=8)
    headsign = models.CharField(max_length=32)
    day = models.CharField(max_length=8)
    stop = models.CharField(max_length=32)
    leave_t = models.CharField(max_length=32)
    stop_time = models.CharField(max_length=32)
    end_t = models.CharField(max_length=32)

    def __str__(self):
        """String representation of the model, can be changed to anything"""
        str_output = f"*****" \
                     f"Route: {self.route}" \
                     f"Headsign: {self.headsign}" \
                     f"Day: {self.day}" \
                     f"Stop: {self.stop}" \
                     f"Leave_time: {self.leave_t}" \
                     f"Stop_time: {self.stop_time}" \
                     f"End_time: {self.end_t}" \
                     f"*****"
        return str_output

    @classmethod
    def scrape(cls):
        # Make api call to gtfs transport for Ireland api and store the result as json in a variable
        scrapers.get_bus_timetable_all()
        print("Finished scraping Dublin_bus_timetable for all stops!")