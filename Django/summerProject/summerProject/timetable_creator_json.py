import json
import os
import DublinBus_current_info
from operator import itemgetter
from django.conf import settings
base = settings.BASE_DIR

def main():
    print("Getting Index")
    index = get_index()
    if index == False:
        print("No file for calendar.txt")
        print("Launching download of text files")
        DublinBus_current_info.main()
        index = get_index()
        if index == False:
            return "No file for calendar.txt available at the minute"
    print("Index Created")
    get_timetable(index)
    get_timetable_all(index)


def get_index():
    #Opens Calendar
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "calendar.txt")
    #Checks if calandar exists in given path returns false if not found
    if os.path.exists(file_location)==False:
        return False
    else:
        #Opens calandar.txt
        with open(file_location, encoding="utf-8-sig") as calendar:
            l = 1
            time_dict = {}
            for line in calendar:
                if l==1:
                    #Creates fields that are read from first line in text file
                    fields = list(line.strip().split(','))
                    l+=1
                else:
                    #reads elements from following lines to apply to fields
                    dates_dict = {}
                    description = list(line.strip().replace('"',"").split(','))
                    count = 0
                    day = []
                    for dates in range(1,8):
                        if description[dates] == "1" and (description[1]!="1" or description[7]!="1"):
                            count += 1
                            day.append(fields[dates][0:3])
                            dates_dict["Days"] = day
                            dates_dict["Start_dt"] = description[8]
                            dates_dict["end_dt"] = description[9]
                        elif description[dates] == "1" and dates!= 1:
                            print(dates)
                            count += 1
                            day.append(fields[dates][0:3])
                            dates_dict["Days"] = day
                            dates_dict["Start_dt"] = description[8]
                            dates_dict["end_dt"] = description[9]
                        else:
                            count +=1
                    time_dict[description[0]] = dates_dict
        return time_dict

def get_timetable(index):
    """Creates timetable for first and last stop only"""
    # Opens paths to json files
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stop_times.json")
    stops_id = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stops.json")
    # Initialises dictionaries and counter
    bus_times = {}
    stops_dict = {}
    count = 0
    # Checks if stop_times.json exists
    if os.path.exists(file_location)==False:
        return False
    else:
        # Opens stops.json file
        with open(stops_id, encoding="utf-8-sig") as out_file:
            stop_id = json.loads(out_file.read())
        # Iterates through it to create a dictionary for stop id to stop
        for id in stop_id:
            stops_dict[stop_id[id]["stop_id"]] = id
        # Opens stops_times.json
        with open(file_location, encoding="utf-8-sig") as out_file:
            timetable = json.loads(out_file.read())
        for stop_time in timetable:
            date_dict = {}
            stop_dict_create = {}
            dir_dict = {}
            # If stop sequence is 1
            if timetable[stop_time]["stop_sequence"] == "1":
                trip_id = timetable[stop_time]["trip_id"]
                trip_id = list(trip_id.strip().split("."))
                date = trip_id[1]
                # Works for dates until October more information is needed how these change in time periods to automate
                if date in ["y1007","y1008","y1009"]:
                    route = list(trip_id[2].strip().split("-"))
                    route = route[1]
                    direction = timetable[stop_time]["stop_headsign"]
                    time = timetable[stop_time]["departure_time"]
                    # Splits time into a list with hour, min and sec each being an element
                    check_time = list(time.split(":"))
                    # If time is greater then 24 takes 24 from hours
                    if int(check_time[0]) >= 24:
                        time = "0" + str(int(check_time[0]) - 24) +":"+ str(check_time[1]) + ":"+ str(check_time[2])
                        print(time)
                    stop = stops_dict[timetable[stop_time]["stop_id"]]
                    date = index[date]["Days"]
                    # if a route already exists in dictionary
                    if route in bus_times:
                        # If the direction for that route exists in the route
                        if direction in bus_times[route]:
                            # If the date exists within that direction
                            if date[0] in bus_times[route][direction]:
                                # If the stop exists in that date
                                if stop in bus_times[route][direction][date[0]]:
                                    # If the time already exists in that stop ignore
                                    if time in bus_times[route][direction][date[0]][stop]:
                                        pass
                                    # Else appends that time along the tree checked by the if statement
                                    else:
                                        bus_times[route][direction][date[0]][stop].append(time)
                                        bus_times[route][direction][date[0]][stop] = sorted(bus_times[route][direction][date[0]][stop])
                                # Creates stop and time list in the dictionary
                                else:
                                    bus_times[route][direction][date[0]][stop] = [time]
                            # Creates stop and time list in separate dictionary then creates a new date key for the path with the stop dictionary
                            else:
                                stop_dict_create[stop] = [time]
                                bus_times[route][direction][date[0]] = stop_dict_create
                        # New stop dictionary saved to new date dictionary saved to main dictionary with new direction
                        else:
                            stop_dict_create[stop] = [time]
                            date_dict[date[0]] = stop_dict_create
                            bus_times[route][direction] = date_dict
                    # Creates a new entry in the main dictionary
                    else:
                        count = count + 1
                        stop_dict_create[stop] = [time]
                        date_dict[date[0]] = stop_dict_create
                        dir_dict[direction] = date_dict
                        bus_times[route] = dir_dict

    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "bus_times")
    #Writes Json file for bus timetable data
    out_file = open(file_location+".json", "w")
    json.dump(bus_times, out_file, indent=4)
    out_file.close()
    #Checks number of routes timetable has been created for
    print(count, "bus route timetables found.")

def get_timetable_all(index):
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stop_times.json")
    stops_id = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stops.json")
    bus_times = {}
    stops_dict = {}
    count = 0
    if os.path.exists(file_location)==False:
        return False
    else:
        #Opens stops.json
        with open(stops_id, encoding="utf-8-sig") as out_file:
            stop_id = json.loads(out_file.read())
        #Iterates through the id's in stops.json
        for id in stop_id:
            stops_dict[stop_id[id]["stop_id"]] = id
        #Opens stop_times.json
        with open(file_location, encoding="utf-8-sig") as out_file:
            timetable = json.loads(out_file.read())
        for stop_time in timetable:
            date_dict = {}
            stop_dict_create = {}
            dir_dict = {}
            # Saves first stop time as first_stop
            if timetable[stop_time]["stop_sequence"] == "1":
                first_stop =  timetable[stop_time]["arrival_time"]
                check_first_time = list(first_stop.split(":"))
                # If first_stop time is greater then 24 takes 24 from hours
                if int(check_first_time[0]) >= 24:
                    first_stop = "0" + str(int(check_first_time[0]) - 24) + ":" + str(check_first_time[1]) + ":" + str(check_first_time[2])
            trip_id = timetable[stop_time]["trip_id"]
            trip_id = list(trip_id.strip().split("."))
            date = trip_id[1]
            # Works for dates until October more information is needed how these change in time periods to automate
            if date in ["y1007","y1008","y1009"]:
                route = list(trip_id[2].strip().split("-"))
                route = route[1]
                direction = timetable[stop_time]["stop_headsign"]
                time = timetable[stop_time]["departure_time"]
                check_time = list(time.split(":"))
                # If time is greater then 24 takes 24 from hours
                if int(check_time[0]) >= 24:
                    time = "0" + str(int(check_time[0]) - 24) + ":" + str(check_time[1]) + ":" + str(check_time[2])
                stop = stops_dict[timetable[stop_time]["stop_id"]]
                date = index[date]["Days"]
                # if a route already exists in dictionary
                if route in bus_times:
                    # If the direction for that route exists in the route
                    if direction in bus_times[route]:
                        # If the date exists within that direction
                        if date[0] in bus_times[route][direction]:
                            # If the stop exists in that date
                            if stop in bus_times[route][direction][date[0]]:
                                # If the time already exists in that stop ignore
                                if [first_stop, time] in bus_times[route][direction][date[0]][stop]:
                                    pass
                                # Else appends that first stop time,time along the tree checked by the if statement
                                else:
                                    bus_times[route][direction][date[0]][stop].append([first_stop, time])
                                    bus_times[route][direction][date[0]][stop] = (sorted(bus_times[route][direction][date[0]][stop], key=itemgetter(0)))
                            # Creates times for a new stop
                            else:
                                bus_times[route][direction][date[0]][stop] = [[first_stop, time]]
                        # Creates times for new stop and date
                        else:
                            stop_dict_create[stop] = [[first_stop, time]]
                            bus_times[route][direction][date[0]] = stop_dict_create
                    # Creates times for new stop, date and direction
                    else:
                        stop_dict_create[stop] = [[first_stop, time]]
                        date_dict[date[0]] = stop_dict_create
                        bus_times[route][direction] = date_dict
                # Creates times for new stop, date, direction and route
                else:
                    count = count + 1
                    stop_dict_create[stop] = [[first_stop, time]]
                    date_dict[date[0]] = stop_dict_create
                    dir_dict[direction] = date_dict
                    bus_times[route] = dir_dict

    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "bus_times")
    #Writes Json file for bus timetable data
    for i in bus_times:
        out_file = open(file_location+"/" + i + "_timetable.json", "w")
        json.dump(bus_times[i], out_file, indent=4)
    out_file.close()
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files")
    # Writes Json file for bus timetable data
    out_file = open(file_location + "/bus_times_all.json", "w")
    json.dump(bus_times, out_file, indent=4)
    out_file.close()
    #Checks number of routes timetable has been created for
    print(count, "bus route timetables found.")
