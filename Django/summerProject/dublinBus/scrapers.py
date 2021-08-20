# Import our models so we can reference them when creating instances of the model and write to db
import os
from django.conf import settings # This allows us to import base directory which we can use for read/write operations
from . import models
import requests
from datetime import datetime
import urllib.request, urllib.parse, urllib.error, json
from urllib.request import urlopen
from summerProject import logins

def get_current_weather():
    """
    Function to make an api call to openweather for current weather results at hard-coded location, returns it as json
    """
    latitude = '53.349805'
    longitude = '-6.26031'
    weather_key = "a50cf221b9fb108b0ae5f652642a0b11"
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

        weather_main=weather_json['weather'][0]['main'],
        weather_description=weather_json['weather'][0]['description'],
        weather_icon=weather_json['weather'][0]['icon'],
        weather_icon_url='http://openweathermap.org/img/wn/{}@2x.png'.format(weather_json['weather'][0]['icon']),

        main_temp=weather_json['main']['temp'],
        weather_id=weather_json['weather'][0]['id'],

    )
    # Store the object which represents a row in our table into the database table
    latestUpdate.save()

def get_weather_forecast():
    """
    Function to make an api call to openweather for 3 hour forecast for next 5 days at hard-coded location, returns it as json
    """
    latitude = '53.349805'
    longitude = '-6.26031'
    weather_key = "a50cf221b9fb108b0ae5f652642a0b11"
    weather_by_coordinates = 'http://api.openweathermap.org/data/2.5/forecast'
    r = requests.get(weather_by_coordinates, params={"APPID": weather_key, "lat": latitude, "lon": longitude})
    weather_json = r.json()
    return weather_json

def write_weather_forecast(weather_json):
    """
    Method to make a WeaetherForecast object from a given json object
    and then writes this object to our WeatherForecast model
    """
    # Make an instance of the model for each 3 hourly forecast for the next 5 days
    # Store all these to a list and then bulk add all from the list to the db
    models.WeatherForecast.objects.all().delete()
    entries = []
    for forecast in weather_json['list']:
        latestUpdate = models.WeatherForecast(
            timestamp=int(forecast['dt']),
            dt=datetime.fromtimestamp(int(forecast['dt'])),

            weather_main=forecast['weather'][0]['main'],
            weather_description=forecast['weather'][0]['description'],
            weather_icon=forecast['weather'][0]['icon'],
            weather_icon_url='http://openweathermap.org/img/wn/{}@2x.png'.format(forecast['weather'][0]['icon']),

            main_temp=forecast['main']['temp'],

            weather_id=forecast['weather'][0]['id']
        )
        entries.append(latestUpdate)
    # Store all our entries from the list to the db
    models.WeatherForecast.objects.bulk_create(entries)

def get_current_bus():
    """
    Function to get current data from the gtfs transport for ireland api and return it in json format
    """
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

    # Create list where we will store all our instances of CurrentBus that are generated in the for loop
    entries = []

    # Timestamp is the same for all items in the json object so we can create this and dt outside the loop
    timestamp = transport_data['header']['timestamp']
    with urlopen("https://www.timeapi.io/api/Time/current/zone?timeZone=Europe/Dublin") as url:
        s = url.read()
        dub_t = json.loads(s)
    print(dub_t["dateTime"])
    dub_date_time = dub_t["dateTime"][:-1]
    dub_date_time = datetime.strptime(dub_date_time.replace("T", " "), '%Y-%m-%d %H:%M:%S.%f')
    dt = dub_date_time

    base = settings.BASE_DIR
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "routes.json")
    with open(file_location) as routes:
        route_obj = json.load(routes)
        routes.close()
        route_list = []
    for i in route_obj:
        route_list.append(route_obj[i]['route_id'])

    # loop through all the entries in 'entity' and create a CurrentBus object for each one before saving to db
    for i in transport_data['entity']:
        trip = i["trip_update"]["trip"]
        if trip["route_id"] in route_list:
            temp_id = i["id"]
            temp_route_id = trip["route_id"]
            temp_schedule = trip["schedule_relationship"]
            temp_start_t = trip["start_time"]
            temp_start_d = trip["start_date"]
            # Now loop through all trip updates within the current trip
            try:
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
                            temp_delay = 0
            except:
                temp_stop_id = None
                temp_delay = None

            # Regardless of what happened in above try/except blocks we want to insert the row by creating the instance regardlesss
            finally:
                # Create one instance CurrentBus for each nested for loop
                latestUpdate = models.CurrentBus(
                    timestamp=timestamp,
                    dt=dt,
                    trip_id=temp_id,
                    direction=temp_id[-1],
                    route_id=temp_route_id,
                    route=list(temp_route_id.split("-"))[1],
                    schedule=temp_schedule,
                    start_t=temp_start_t,
                    start_d=temp_start_d,
                    stop_id=temp_stop_id,
                    delay=temp_delay,
                )
                # Now append this instance to our list of entries
                entries.append(latestUpdate)
        else:
            pass
    # Save all our entries to the database
    models.CurrentBus.objects.bulk_create(entries)

def get_bus_stop():
    # Read file with all stops
    base = settings.BASE_DIR
    file_location = os.path.join(base, "dublinBus", "stops.txt")
    f = open(file_location, "r")
    # Truncate table
    models.BusStops.objects.all().delete()

    count = 0
    entries = []
    while (True):
        try:
            # read next line
            line = f.readline()
            # if line is empty, you are done with all lines in the file
            if not line:
                break

            x = line.split('","')
            y = x[1].split(", stop ")
            # Check that the string for longitude and latitude are valid before casting to float
            temp_stop_lat = x[2]
            temp_stop_lon = x[3]

            # Remove inverted commas and new line characters from string so it can be converted to float
            temp_stop_lat = temp_stop_lat.replace('"', '')
            temp_stop_lat = temp_stop_lat.strip()
            # Cast to float
            temp_stop_lat = float(temp_stop_lat)

            # Remove inverted commas and new line characters from string so it can be converted to float
            temp_stop_lon = temp_stop_lon.replace('"', '')
            temp_stop_lon = temp_stop_lon.strip()
            # Cast to float
            temp_stop_lon = float(temp_stop_lon)

            latestUpdate = models.BusStops(
                stop_id=x[0],
                stop_name=y[0],
                stop_number=y[1],
                stop_lat=temp_stop_lat,
                stop_lon=temp_stop_lon
            )
            entries.append(latestUpdate)
        except Exception as e:
            count +=1
            print(e)
    # close file
    f.close
    models.BusStops.objects.bulk_create(entries)
    print("Number of stations failing:",count)

def get_bus_timetable():
    """Uses information obtained through the GTFS to build a current timetable
    Note please run timetable_creator_json to access the data"""

    base = settings.BASE_DIR
    file_location = os.path.join(base, "dublinBus", "json_files", "bus_times.json")
    with open(file_location, encoding="utf-8-sig") as out_file:
        timetable = json.loads(out_file.read())

    # Truncate table
    models.Current_timetable.objects.all().delete()
    entries = []
    for routes in timetable:
        for directions in timetable[routes]:
            for day in timetable[routes][directions]:
                for time in timetable[routes][directions][day]:
                    latestUpdate = models.Current_timetable(
                        route=routes,
                        direction=directions,
                        day=day,
                        leave_t=time
                    )
                    entries.append(latestUpdate)
    models.Current_timetable.objects.bulk_create(entries)

def get_bus_timetable_all():
    base = settings.BASE_DIR
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "bus_times_all.json")
    file_location_stops = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stops.json")
    with open(file_location, encoding="utf-8-sig") as out_file:
        timetable = json.loads(out_file.read())
    models.Current_timetable_all.objects.all().delete()
    entries = []
    for routes in timetable:
        for directions in timetable[routes]:
            for day in timetable[routes][directions]:
                first_last = {}
                for stop in timetable[routes][directions][day]:
                    for time in range(0, len(timetable[routes][directions][day][stop])):
                        if timetable[routes][directions][day][stop][time][0] in first_last and timetable[routes][directions][day][stop][time][1] > first_last[timetable[routes][directions][day][stop][time][0]]:
                            first_last[timetable[routes][directions][day][stop][time][0]] = timetable[routes][directions][day][stop][time][1]
                        elif timetable[routes][directions][day][stop][time][0] not in first_last:
                            first_last[timetable[routes][directions][day][stop][time][0]] = timetable[routes][directions][day][stop][time][1]
                        elif timetable[routes][directions][day][stop][time][1] <= first_last[timetable[routes][directions][day][stop][time][0]]:
                            pass
                        else:
                            first_last[timetable[routes][directions][day][stop][time][0]] = timetable[routes][directions][day][stop][time][1]

                for stop in timetable[routes][directions][day]:
                    for time in range(0, len(timetable[routes][directions][day][stop])):
                        latestUpdate = models.Current_timetable_all (
                            route=routes,
                            headsign=directions,
                            day=day,
                            stop = stop,
                            leave_t=timetable[routes][directions][day][stop][time][0],
                            stop_time=timetable[routes][directions][day][stop][time][1],
                            end_t=first_last[timetable[routes][directions][day][stop][time][0]]
                        )
                        entries.append(latestUpdate)
                        if len(entries)==1000:
                            models.Current_timetable_all.objects.bulk_create(entries)
                            entries = []
                            print("successful_entry")
    models.Current_timetable_all.objects.bulk_create(entries)