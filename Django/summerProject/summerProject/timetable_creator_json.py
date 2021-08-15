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
        print(time_dict)
        return time_dict

def get_timetable(index):
    #Opens paths to json files
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stop_times.json")
    stops_id = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stops.json")
    #Initialises dictionaries and counter
    bus_times = {}
    stops_dict = {}
    count = 0
    #Checks if stop_times.json exists
    if os.path.exists(file_location)==False:
        return False
    else:
        with open(stops_id, encoding="utf-8-sig") as out_file:
            stop_id = json.loads(out_file.read())
        for id in stop_id:
            stops_dict[stop_id[id]["stop_id"]] = id
        with open(file_location, encoding="utf-8-sig") as out_file:
            timetable = json.loads(out_file.read())
        for stop_time in timetable:
            date_dict = {}
            stop_dict_create = {}
            dir_dict = {}
            #If stop sequence is 1
            if timetable[stop_time]["stop_sequence"] == "1":
                trip_id = timetable[stop_time]["trip_id"]
                trip_id = list(trip_id.strip().split("."))
                date = trip_id[1]
                #****************************** NB- Hard coded needs to be fixed *****************************
                if date in ["y1007","y1008","y1009"]:
                    route = list(trip_id[2].strip().split("-"))
                    route = route[1]
                    direction = timetable[stop_time]["stop_headsign"]
                    time = timetable[stop_time]["departure_time"]
                    check_time = list(time.split(":"))
                    if int(check_time[0]) >= 24:
                        time = str(int(check_time[0]) - 24) +":"+ str(check_time[1]) + ":"+ str(check_time[2])
                    stop = stops_dict[timetable[stop_time]["stop_id"]]
                    date = index[date]["Days"]
                    if route in bus_times:
                        success_dir = 0
                        if direction in bus_times[route]:
                            if date[0] in bus_times[route][direction]:
                                if stop in bus_times[route][direction][date[0]]:
                                    if time in bus_times[route][direction][date[0]][stop]:
                                        pass
                                    else:
                                        bus_times[route][direction][date[0]][stop].append(time)
                                        bus_times[route][direction][date[0]][stop] = sorted(bus_times[route][direction][date[0]][stop])
                                else:
                                    bus_times[route][direction][date[0]][stop] = [time]
                            else:
                                stop_dict_create[stop] = [time]
                                #date_dict[date[0]] = stop_dict_create
                                bus_times[route][direction][date[0]] = stop_dict_create
                        else:
                            stop_dict_create[stop] = [time]
                            date_dict[date[0]] = stop_dict_create
                            #dir_dict[direction] = date_dict
                            bus_times[route][direction] = date_dict
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
        with open(stops_id, encoding="utf-8-sig") as out_file:
            stop_id = json.loads(out_file.read())
        for id in stop_id:
            stops_dict[stop_id[id]["stop_id"]] = id
        with open(file_location, encoding="utf-8-sig") as out_file:
            timetable = json.loads(out_file.read())
        for stop_time in timetable:
            date_dict = {}
            stop_dict_create = {}
            dir_dict = {}
            if timetable[stop_time]["stop_sequence"] == "1":
                first_stop =  timetable[stop_time]["arrival_time"]
                check_first_time = list(first_stop.split(":"))
                if int(check_first_time[0]) >= 24:
                    first_stop = str(int(check_first_time[0]) - 24) + ":" + str(check_first_time[1]) + ":" + str(check_first_time[2])
            trip_id = timetable[stop_time]["trip_id"]
            trip_id = list(trip_id.strip().split("."))
            date = trip_id[1]
            #****************************** NB- Hard coded needs to be fixed *****************************
            if date in ["y1003","y1004","y1005"]:
                route = list(trip_id[2].strip().split("-"))
                route = route[1]
                direction = timetable[stop_time]["stop_headsign"]
                time = timetable[stop_time]["departure_time"]
                check_time = list(time.split(":"))
                if int(check_time[0]) >= 24:
                    time = str(int(check_time[0]) - 24) + ":" + str(check_time[1]) + ":" + str(check_time[2])
                stop = stops_dict[timetable[stop_time]["stop_id"]]
                date = index[date]["Days"]
                if route in bus_times:
                    success_dir = 0
                    if direction in bus_times[route]:
                        if date[0] in bus_times[route][direction]:
                            if stop in bus_times[route][direction][date[0]]:
                                if [first_stop, time] in bus_times[route][direction][date[0]][stop]:
                                    pass
                                else:
                                    bus_times[route][direction][date[0]][stop].append([first_stop, time])
                                    bus_times[route][direction][date[0]][stop] = (sorted(bus_times[route][direction][date[0]][stop], key=itemgetter(0)))
                            else:
                                bus_times[route][direction][date[0]][stop] = [[first_stop, time]]
                        else:
                            if time > "24:00:00":
                                print(time)
                            stop_dict_create[stop] = [[first_stop, time]]
                            #date_dict[date[0]] = stop_dict_create
                            bus_times[route][direction][date[0]] = stop_dict_create
                    else:
                        stop_dict_create[stop] = [[first_stop, time]]
                        date_dict[date[0]] = stop_dict_create
                        #dir_dict[direction] = date_dict
                        bus_times[route][direction] = date_dict
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
