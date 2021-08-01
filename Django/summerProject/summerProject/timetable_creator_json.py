import json
import os
from . import DublinBus_current_info
from django.conf import settings
import time
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
                        if description[dates] == "1":
                            count += 1
                            day.append(fields[dates][0:3])
                            dates_dict["Days"] = day
                            dates_dict["Start_dt"] = description[8]
                            dates_dict["end_dt"] = description[9]
                    time_dict[description[0]] = dates_dict
        return time_dict

def get_timetable(index):
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
                trip_id = timetable[stop_time]["trip_id"]
                trip_id = list(trip_id.strip().split("."))
                date = trip_id[1]
                #****************************** NB- Hard coded needs to be fixed *****************************
                if date in ["y1003","y1004","y1005"]:
                    route = list(trip_id[2].strip().split("-"))
                    route = route[1]
                    direction = timetable[stop_time]["stop_headsign"]
                    time = timetable[stop_time]["departure_time"]
                    stop = stops_dict[timetable[stop_time]["stop_id"]]
                    date = index[date]["Days"]
                    if route in bus_times:
                        success_dir = 0
                        for i in range(0,len(bus_times[route])):
                            if direction in bus_times[route][i]:
                                success_dir = 1
                                success_dt = 0
                                for j in range(0,len(bus_times[route][i][direction])):
                                    if date[0] in bus_times[route][i][direction][j]:
                                        success_dt = 1
                                        success_stop = 0
                                        for k in range(0, len(bus_times[route][i][direction][j][date[0]])):
                                            if stop in bus_times[route][i][direction][j][date[0]][k]:
                                                success_stop = 1
                                                if time in bus_times[route][i][direction][j][date[0]][k][stop]:
                                                    pass
                                                else:
                                                    bus_times[route][i][direction][j][date[0]][k][stop].append(time)
                                                    bus_times[route][i][direction][j][date[0]][k][stop] = sorted(bus_times[route][i][direction][j][date[0]][k][stop])
                                            elif stop not in bus_times[route][i][direction][j][date[0]][k] and k == (len(bus_times[route][i][direction][j][date[0]]) - 1) and success_stop == 0:
                                                stop_dict_create[stop] = [time]
                                                bus_times[route][i][direction][j][date[0]].append(stop_dict_create)
                                    elif date[0] not in bus_times[route][i][direction][j] and j == (len(bus_times[route][i][direction]) - 1) and success_dt == 0:
                                        stop_dict_create[stop] = [time]
                                        date_dict[date[0]] = [stop_dict_create]
                                        bus_times[route][i][direction].append(date_dict)
                            elif (direction not in bus_times[route][i]) and i == len(bus_times[route]) -1 and success_dir == 0:
                                stop_dict_create[stop] = [time]
                                date_dict[date[0]] = [stop_dict_create]
                                dir_dict[direction] = [date_dict]
                                bus_times[route].append(dir_dict)
                    else:
                        count = count + 1
                        stop_dict_create[stop] = [time]
                        date_dict[date[0]] = [stop_dict_create]
                        dir_dict[direction] = [date_dict]
                        bus_times[route] = [dir_dict]
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "bus_times")
    #Writes Json file for bus timetable data
    out_file = open(file_location+".json", "w")
    json.dump(bus_times, out_file, indent=4)
    out_file.close()
    #Checks number of routes timetable has been created for
    print(count, "bus route timetables found.")

