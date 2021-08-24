import requests
from zipfile import ZipFile
import json
import os
from django.conf import settings
base = settings.BASE_DIR
def main():
    download()
    files = ['stop_times.txt','routes.txt','shapes.txt','stops.txt']
    for i in files:
        json_convertor(i)


def download():
    print('Download Starting...')

    url = 'https://www.transportforireland.ie/transitData/google_transit_dublinbus.zip'

    r = requests.get(url)

    filename = url.split('/')[-1]  # this will take only -1 splitted part of the url
    with open(filename, 'wb') as output_file:
        output_file.write(r.content)
    # Create a ZipFile Object and load sample.zip in it
    with ZipFile(filename, 'r') as zipObj:
       # Extract all the contents of zip file in current directory

       file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", )
       zipObj.extractall(path=file_location)
    print('Download Completed!!!')
    os.remove(filename)

def json_convertor(filename):

    """Converts text files to custom json files"""

    # resultant dictionary
    dict1 = {}
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", filename)
    with open(file_location, encoding="utf-8-sig") as fh:
        # count variable for id
        l = 1
        if filename == "stops.txt":
            bus_dict = route_to_stop()
        elif filename == "routes.txt":
            bus_dict = route_destinations()
        for line in fh:
            # Line 1 reads headers of files
            if (l==1):
                # Comma present in stops.txt for stop name that separates name with number
                # Extra header present for added information of routes
                if filename == "stops.txt":
                    ext_line = "stop_id,stop_name,stop_num,stop_lat,stop_lon,routes"
                    fields = list(ext_line.strip().split(','))
                # Headers from routes.txt file and direction
                elif filename == "routes.txt":
                    fields = list(line.strip().split(','))
                    fields.append("direction")
                # Headers from txt files
                else:
                    fields = list(line.strip().split(','))
            # Lines after headers
            if (l!=1):
                # reading line by line from the text file
                description = list(line.strip('"').strip('\n').split(','))
                count = 0
                # removes commas and single quote marks from lines
                for i in description:
                    description[count] = i.replace('"','')
                    count +=1
                # for automatic creation of id
                id = 'id' + str(l)
                # loop variable
                i = 0
                dict2 = {}
                while i < len(fields):
                    # dictionary for each id
                    # Error in stops.txt file were inconsistent naming convention, catches when missing stop number
                    if filename == "stops.txt" and len(description)==4 :
                        if i==2:
                            dict2[fields[i]] = "null"
                        elif i==5:
                            dict2[fields[i]] = bus_dict[description[0]]
                        elif i>2:
                            dict2[fields[i]] = description[i-1].lstrip()
                        else:
                            dict2[fields[i]] = description[i].lstrip()
                    # id saves information from bus dict
                    elif filename == "stops.txt" and i==5:
                        dict2[fields[i]] = bus_dict[description[0]]
                    # id saves information from bus dict
                    elif filename == "routes.txt" and i==5:
                        # Checks bus dict for a route
                        if description[2] in bus_dict:
                            dict2[fields[i]] = bus_dict[description[2]]
                        # Checks bus dict for a route.upper
                        elif description[2].upper() in bus_dict:
                            dict2[fields[i]] = bus_dict[description[2].upper()]
                    # Changes route name to uppercase
                    elif filename == "routes.txt" and i == 2:
                        dict2[fields[i]] = description[i].lstrip().upper()
                    # Appends rest of the values to dictionary
                    else:
                        dict2[fields[i]] = description[i].lstrip()
                    i = i + 1
                # appending the record of each id to main dictionary
                if filename == "routes.txt" and len(dict2) == 5:
                    pass
                else:
                    if filename == "routes.txt":
                        dict1[description[2].upper()] = dict2
                    elif filename == "stops.txt":
                        dict1[description[2].lstrip(" stop ")] = dict2
                    else:
                        dict1[id] = dict2
            l = l + 1
    # Converts stop id to stop number
    if filename == "stops.txt":
        dict1 = convert_stop_id_to_num(dict1)
    # creating json file
    filename = filename.strip('.txt')
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", filename)
    out_file = open(file_location+".json", "w")
    json.dump(dict1, out_file, indent=4)
    out_file.close()
    print("Finished saving", filename + ".json")

def route_to_stop():

    """Gets the information displayed withing stops.json routes"""

    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stop_times.json")
    # Open stop_times json file
    with open(file_location, encoding="utf-8-sig") as out_file:
        stop_times = json.loads(out_file.read())
    out_file.close()
    bus_dict = {}
    bus_dir = {}
    id_list =[]
    first_line = True
    # Iterates through all id's in stop times
    for id in stop_times:
        # If it is the first stop in sequence
        if stop_times[id]["stop_sequence"] == "1":
            # Enters first line false after the first iteration
            if first_line == False:
                # Appends the last sequence stop id to the list in bus dict
                for sub_id in id_list:
                    dir_list = bus_dict[sub_id]
                    counter = 0
                    for route in dir_list:
                        if route[0] == prev_route and route[1] == prev_headsign and route[4] == stop_sequence and len(route)==5:
                            route.append(stop_sequence_last)
                            # Creates the percent of the route completed at each stop
                            route[3] = float(route[3])/float(prev_dist)
                            temp_list = route
                            dir_list[counter] = temp_list
                            bus_dict[sub_id] = dir_list
                        counter += 1
                id_list = []
                last_stop = stop_sequence_last
            stop_sequence = stop_times[id]["stop_id"]
            first_line = False
        # If the stop id exists in the keys of bus_dict
        if stop_times[id]["stop_id"] in bus_dict.keys():
            bus_num = list(stop_times[id]["trip_id"].split("."))
            bus_num = list(bus_num[2].split("-"))
            route_id = bus_num[1]
            check_list = [bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence]
            list_check = False
            # Iterates through lists saved in bus dictionary
            for sub_list in bus_dict[stop_times[id]["stop_id"]]:
                # Contains route, head-sign, stop sequence, percent of route, start stop, last stop
                if len(sub_list) == 6:
                    # Checks that route, head-sign, stop sequence, start stop is same as defined before
                    if check_list[0] == sub_list[0] and check_list[1] == sub_list[1] and check_list[2] == sub_list[2] and check_list[4] == sub_list[4]:
                        list_check = True
            # If list check is true pass
            if list_check == True:
                pass
            # If list in bus dictionary with key from stop_times.json
            elif [bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"],stop_sequence] in bus_dict[stop_times[id]["stop_id"]]:
                pass
            else:
                list_1 = bus_dict[stop_times[id]["stop_id"]]
                # If route in bus direction dictionary keys
                if bus_num[1] in bus_dir.keys():
                    # If headsign same as that in bus direction
                    if bus_dir[route_id] == stop_times[id]["stop_headsign"]:
                        bus_list = [bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence]
                        list_1.append(bus_list)
                        bus_dict[stop_times[id]["stop_id"]] = list_1
                    # Else append the elements to list 1 and save to bus dict
                    else:
                        list_1.append([bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence])
                        bus_dict[stop_times[id]["stop_id"]] = list_1
                # Else save route to bus direction keys and append the list to bus dictionary
                else:
                    list_1.append([bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence])
                    bus_dict[stop_times[id]["stop_id"]] = list_1
                    bus_dir[bus_num[1]] = stop_times[id]["stop_headsign"]
        # If stop ID not in bus dict
        else:
            bus_num = list(stop_times[id]["trip_id"].split("."))
            bus_num = list(bus_num[2].split("-"))
            # If bus route in bus directions
            if bus_num[1] in bus_dir:
                if bus_dir[bus_num[1]] == stop_times[id]["stop_headsign"]:
                    bus_dict[stop_times[id]["stop_id"]] = [[bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence]]
                else:
                    bus_dict[stop_times[id]["stop_id"]] = [[bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence]]
            else:
                bus_dir[bus_num[1]] = stop_times[id]["stop_headsign"]
                bus_dict[stop_times[id]["stop_id"]] = [[bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence]]
        stop_sequence_last = stop_times[id]["stop_id"]
        id_list.append(stop_sequence_last)
        # Saves previous values for use in subsequent call
        prev_headsign = stop_times[id]["stop_headsign"]
        prev_route = list(stop_times[id]["trip_id"].split("."))
        prev_route = list(prev_route[2].split("-"))
        prev_route = prev_route[1]
        prev_dist = stop_times[id]["shape_dist_traveled"]
    for id in bus_dict:
        del_list = []
        # Saves values contained at each part of the list for each id
        for i in range(0, len(bus_dict[id])):
            save_route = bus_dict[id][i][0]
            save_start = bus_dict[id][i][4]
            save_end = bus_dict[id][i][1]
            save_seq = bus_dict[id][i][2]
            save_ele = i
            # Repeats for loop
            for ele in range(0, len(bus_dict[id])):
                if bus_dict[id][ele][0] == save_route and bus_dict[id][ele][4] == save_start and bus_dict[id][ele][1] == save_end and i != ele:
                    # If sequence was less then saved number and list not in delete lists value from index added to delete list
                    if bus_dict[id][ele][2] < save_seq and ele not in del_list:
                        del_list.append(ele)
                    # Saves index value of saved values if save sequence is less
                    elif bus_dict[id][ele][2] > save_seq and save_ele not in del_list:
                        del_list.append(save_ele)
        # Deletes repeated values from the bus dictionary of the same route
        for j in sorted(del_list, reverse=True):
            del bus_dict[id][j]
    return bus_dict

def route_destinations():

    """Creates directions in routes, whether a route is inbound or outbound"""

    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files",
                                 "stop_times.json")
    # Open stop_times json file
    with open(file_location) as out_file:
        stop_times = json.loads(out_file.read())
    out_file.close()
    bus_dict = {}
    for id in stop_times:
        bus_route = list(stop_times[id]["trip_id"].split("."))
        bus_num = list(bus_route[2].split("-"))
        route_id = bus_num[1]
        route_id = route_id.strip("'")
        route_id_dir = bus_route[4]
        check = 0
        if route_id in bus_dict:
            for i in bus_dict[route_id]:
                # If checked route exists already check changes to 1
                if i == [stop_times[id]["stop_headsign"].lstrip(), route_id_dir]:
                    check = 1
            # If exists ignores
            if check == 1:
                pass
            # Else appends to bus dictionary
            else:
                bus_dict[route_id].append([stop_times[id]["stop_headsign"].lstrip(), route_id_dir])
        # direction not in bus dictionary adds direction to bus dictionary
        else:
            bus_dict[route_id]=[[stop_times[id]["stop_headsign"].lstrip(), route_id_dir]]
    return bus_dict

def convert_stop_id_to_num(dict1):

    """Changes stop id to stop number"""

    stops_id = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stops.json")
    stops_dict = {}
    with open(stops_id, encoding="utf-8-sig") as out_file:
        stop_id = dict1
    for id in stop_id:
        stops_dict[stop_id[id]["stop_id"]] = id
    for stop in stop_id:
        for route in range(0, len(stop_id[stop]["routes"])):
            stop_id[stop]["routes"][route][4] = stops_dict[stop_id[stop]["routes"][route][4]]
            stop_id[stop]["routes"][route][5] = stops_dict[stop_id[stop]["routes"][route][5]]
    return stop_id
