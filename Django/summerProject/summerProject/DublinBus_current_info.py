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
            if (l==1):
                #Comma present in stops.txt for stop name that seperates name with number
                if filename == "stops.txt":
                    ext_line = "stop_id,stop_name,stop_num,stop_lat,stop_lon,routes"
                    fields = list(ext_line.strip().split(','))
                elif filename == "routes.txt":
                    fields = list(line.strip().split(','))
                    fields.append("direction")
                else:
                    fields = list(line.strip().split(','))
            if (l!=1):
                # reading line by line from the text file
                description = list(line.strip('"').strip('\n').split(','))
                count = 0
                for i in description:
                    description[count] = i.replace('"','')
                    count +=1
                # for automatic creation of id
                id = 'id' + str(l)
                # loop variable
                i = 0
                dict2 = {}
                while i < len(fields):
                    #dictionary for each id
                    #Error in stops.txt file were inconsistent naming convention, catches when missing stop number
                    if filename == "stops.txt" and len(description)==4 :
                        if i==2:
                            dict2[fields[i]] = "null"
                        elif i==5:
                            dict2[fields[i]] = bus_dict[description[0]]
                        elif i>2:
                            dict2[fields[i]] = description[i-1].lstrip()
                        else:
                            dict2[fields[i]] = description[i].lstrip()

                    elif filename == "stops.txt" and i==5:
                        dict2[fields[i]] = bus_dict[description[0]]
                    elif filename == "routes.txt" and i==5:
                        if description[2] in bus_dict:
                            dict2[fields[i]] = bus_dict[description[2]]
                        elif description[2].upper() in bus_dict:
                            dict2[fields[i]] = bus_dict[description[2].upper()]
                    elif filename == "routes.txt" and i == 2:
                        dict2[fields[i]] = description[i].lstrip().upper()
                    else:
                        dict2[fields[i]] = description[i].lstrip()
                    i = i + 1
                # appending the record of each id
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
    if filename == "stops.txt":
        dict1 = convert_stop_id_to_num(dict1)
    # creating json file
    filename = filename.strip('.txt')
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", filename)
    # out_file = open("../../summerProject/dublinBus/static/dublinBus/Dublin_bus_info/json_files/"+filename+".json", "w")
    out_file = open(file_location+".json", "w")
    json.dump(dict1, out_file, indent=4)
    out_file.close()
    print("Finished saving", filename + ".json")

def route_to_stop():
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files", "stop_times.json")
    #Open stop_times json file
    with open(file_location, encoding="utf-8-sig") as out_file:
        stop_times = json.loads(out_file.read())
    out_file.close()
    bus_dict = {}
    bus_dir = {}
    id_list =[]
    first_line = True
    #Iterates through all id's in stop times
    for id in stop_times:
        if stop_times[id]["stop_sequence"] == "1":
            if first_line == False:
                for sub_id in id_list:
                    dir_list = bus_dict[sub_id]
                    counter = 0
                    for route in dir_list:
                        if route[0] == prev_route and route[1] == prev_headsign and route[4] == stop_sequence and len(route)==5:
                            route.append(stop_sequence_last)
                            route[3] = float(route[3])/float(prev_dist)
                            temp_list = route
                            dir_list[counter] = temp_list
                            bus_dict[sub_id] = dir_list
                        counter += 1
                id_list = []
                last_stop = stop_sequence_last
            stop_sequence = stop_times[id]["stop_id"]
            first_line = False
        if stop_times[id]["stop_id"] in bus_dict.keys():
            bus_num = list(stop_times[id]["trip_id"].split("."))
            bus_num = list(bus_num[2].split("-"))
            route_id = bus_num[1]
            check_list = [bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence]
            list_check = False
            for sub_list in bus_dict[stop_times[id]["stop_id"]]:
                if len(sub_list)==6:
                    if check_list[0] == sub_list[0] and check_list[1] == sub_list[1] and check_list[2] == sub_list[2] and check_list[4] == sub_list[4]:
                        list_check = True
            if list_check == True:
                pass
            elif [bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"],stop_sequence] in bus_dict[stop_times[id]["stop_id"]]:
                pass
            else:
                list_1 = bus_dict[stop_times[id]["stop_id"]]
                if bus_num[1] in bus_dir.keys():
                    if bus_dir[route_id] == stop_times[id]["stop_headsign"]:
                        bus_list = [bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence]
                        list_1.append(bus_list)
                        bus_dict[stop_times[id]["stop_id"]] = list_1
                    else:
                        list_1.append([bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence])
                        bus_dict[stop_times[id]["stop_id"]] = list_1
                else:
                    list_1.append([bus_num[1], stop_times[id]["stop_headsign"].lstrip(), stop_times[id]["stop_sequence"], stop_times[id]["shape_dist_traveled"], stop_sequence])
                    bus_dict[stop_times[id]["stop_id"]] = list_1
                    bus_dir[bus_num[1]] = stop_times[id]["stop_headsign"]

        else:
            bus_num = list(stop_times[id]["trip_id"].split("."))
            bus_num = list(bus_num[2].split("-"))
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
        prev_headsign = stop_times[id]["stop_headsign"]
        prev_route = list(stop_times[id]["trip_id"].split("."))
        prev_route = list(prev_route[2].split("-"))
        prev_route = prev_route[1]
        prev_dist = stop_times[id]["shape_dist_traveled"]
    for id in bus_dict:
        del_list = []
        for i in range(0, len(bus_dict[id])):
            save_route = bus_dict[id][i][0]
            save_start = bus_dict[id][i][4]
            save_end = bus_dict[id][i][1]
            save_seq = bus_dict[id][i][2]
            save_ele = i
            for ele in range(0, len(bus_dict[id])):
                if bus_dict[id][ele][0] == save_route and bus_dict[id][ele][4] == save_start and bus_dict[id][ele][1] == save_end and i != ele:
                    if bus_dict[id][ele][2] < save_seq and ele not in del_list:
                        del_list.append(ele)
                    elif bus_dict[id][ele][2] > save_seq and save_ele not in del_list:
                        del_list.append(save_ele)

                #if (float(bus_dict[id][i][4]) - float(int(bus_dict[id][i][4]))) == 0.0 and (float(bus_dict[id][i][5]) - float(int(bus_dict[id][i][5]))) == 0.0:
                #    pass
                #elif ele not in del_list:
                #    del_list.append(ele)
                #    print("here")
        for j in sorted(del_list, reverse = True):
            del bus_dict[id][j]
    return bus_dict

def route_destinations():
    file_location = os.path.join(base, "dublinBus", "static", "dublinBus", "Dublin_bus_info", "json_files",
                                 "stop_times.json")
    # Open stop_times json file
    with open(file_location) as out_file:
        stop_times = json.loads(out_file.read())
    out_file.close()
    bus_dict = {}
    for id in stop_times:
        dir = {}
        bus_route = list(stop_times[id]["trip_id"].split("."))
        bus_num = list(bus_route[2].split("-"))
        route_id = bus_num[1]
        route_id = route_id.strip("'")
        route_id_dir = bus_route[4]
        check = 0
        if route_id in bus_dict:
            for i in bus_dict[route_id]:
                if i == [stop_times[id]["stop_headsign"].lstrip(), route_id_dir]:
                    check = 1
            if check == 1:
                pass
            else:
                bus_dict[route_id].append([stop_times[id]["stop_headsign"].lstrip(), route_id_dir])
        else:
            bus_dict[route_id]=[[stop_times[id]["stop_headsign"].lstrip(), route_id_dir]]
    return bus_dict

def convert_stop_id_to_num(dict1):
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
