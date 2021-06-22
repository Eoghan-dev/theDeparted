# Import our models so we can reference them when creating instances of the model and write to db
from . import models
import requests
from datetime import datetime
import urllib.request, urllib.parse, urllib.error, json
def get_current_weather():
    """
    Method to make an api call to openweather for current weather results, returns it as json
    """
    latitude = '53.349805'
    longitude = '-6.26031'
    weather_key = "7ac118753938be7d1540e9f996c5aab4"
    weather_by_coordinates = 'http://api.openweathermap.org/data/2.5/weather'
    r = requests.get(weather_by_coordinates, params={"APPID": weather_key, "lat": latitude, "lon": longitude})
    weather_json = r.json()
    return weather_json

def write_current_weather(weather_json):
    """
    Method to make a CurrentWeather object from a given json object
    and then writes this object to our CurrentWeather model
    """
    # Make an object for the current update that is being scraped
    latestUpdate = models.CurrentWeather(
        timestamp=int(weather_json['dt']),
        dt=datetime.fromtimestamp(int(weather_json['dt'])),
        coord_lon='53.349805',
        coord_lat='53.349805',

        weather_id=weather_json['weather'][0]['id'],
        weather_main=weather_json['weather'][0]['main'],
        weather_description=weather_json['weather'][0]['description'],
        weather_icon=weather_json['weather'][0]['icon'],
        weather_icon_url='http://openweathermap.org/img/wn/{}@2x.png'.format(weather_json['weather'][0]['icon']),

        base=weather_json['base'],
        main_temp=weather_json['main']['temp'],
        main_feels_like=weather_json['main']['feels_like'],
        main_temp_min=weather_json['main']['temp_min'],
        main_temp_max=weather_json['main']['temp_max'],
        main_pressure=weather_json['main']['pressure'],
        main_humidity=weather_json['main']['humidity'],
        visibility=weather_json['visibility'],

        wind_speed=weather_json['wind']['speed'],
        wind_deg=weather_json['wind']['deg'],

        clouds_all=weather_json['clouds']['all'],

        sys_type=weather_json['sys']['type'],
        sys_id=weather_json['sys']['id'],
        sys_country=weather_json['sys']['country'],
        sys_sunrise=weather_json['sys']['sunrise'],
        sys_sunset=weather_json['sys']['sunset'],

        timezone=weather_json['timezone'],
        id=weather_json['id'],
        name=weather_json['name'],
        cod=weather_json['cod'],
    )
    # Store the object which represents a row in our table into the database table
    latestUpdate.save()

def get_current_bus():
    """Function to get current data from the gtfs transport for ireland api and return it in json format"""
    headers = {
        # Request headers
        'Cache-Control': 'no-cache',
        'x-api-key': '100d436970cb4ed5b1e954c64f541cb0',
    }

    params = urllib.parse.urlencode({
    })

    gtfs = 'https://gtfsr.transportforireland.ie/v1/?format=json'
    r = requests.get(gtfs, params=params, headers=headers)
    data = json.loads(r.content)
    return data

def write_current_bus(transport_data):
    """
    Function to write the results from an API call to gtfs transport for Ireland to our db
    Each trip update for each respective trip will be made into a CurrentBus object and then saved into a respective row
    in the database table. The table gets cleared everytime the function is run before saving new info.
    """
    # Truncate table
    models.CurrentBus.objects.all().delete()

    # Timestamp is the same for all items in the json object so we can create this and dt outside the loop
    timestamp = transport_data['header']['timestamp']
    dt = datetime.fromtimestamp(int(transport_data['header']['timestamp']))

    # loop through all the entries in 'entity' and create a CurrentBus object for each one before saving to db
    for i in transport_data['entity']:
        trip = i["trip_update"]["trip"]
        temp_id = i["id"],
        temp_route_id = trip["route_id"],
        temp_schedule = trip["schedule_relationship"],
        temp_start_t = trip["start_time"],
        temp_start_d = trip["start_date"],
        # Now loop through all trip updates within the current trip
        for j in i["trip_update"]["stop_time_update"]:
            temp_stop_id = j["stop_id"]
            try:
                test = j["departure"]
                temp_delay = test["delay"]
            except:
                try:
                    test = j['arrival']
                    temp_delay = test["delay"]
                except:
                    delay = 0
            temp_delay = test["delay"]
            # Create one instance CurrentBus for each nested for loop
            latestUpdate = models.CurrentBus(
                timestamp=timestamp,
                dt=dt,
                trip_id=temp_id,
                route_id=temp_route_id,
                schedule=temp_schedule,
                start_t=temp_start_t,
                start_d=temp_start_d,
                stop_id=temp_stop_id,
                delay=temp_delay,
            )
            # Now save this instance with the current trip update to the database
            latestUpdate.save()