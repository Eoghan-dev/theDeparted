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
                    else:
                        dict2[fields[i]] = description[i]
                    i = i + 1
                # appending the record of each id
                dict1[id] = dict2
            l = l + 1
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
    #Iterates through all id's in stop times
    for id in stop_times:
        if stop_times[id]["stop_id"] in bus_dict.keys():
            bus_num = list(stop_times[id]["trip_id"].split("."))
            bus_num = list(bus_num[2].split("-"))
            route_id = bus_num[1]
            if [bus_num[1], stop_times[id]["stop_headsign"].lstrip()] in bus_dict[stop_times[id]["stop_id"]]:
                pass
            else:
                list_1 = bus_dict[stop_times[id]["stop_id"]]
                if bus_num[1] in bus_dir.keys():
                    if bus_dir[route_id] == stop_times[id]["stop_headsign"]:
                        bus_list = [bus_num[1], stop_times[id]["stop_headsign"].lstrip()]
                        list_1.append(bus_list)
                        bus_dict[stop_times[id]["stop_id"]] = list_1
                    else:
                        list_1.append([bus_num[1], stop_times[id]["stop_headsign"].lstrip()])
                        bus_dict[stop_times[id]["stop_id"]] = list_1
                else:
                    list_1.append([bus_num[1], stop_times[id]["stop_headsign"].lstrip()])
                    bus_dict[stop_times[id]["stop_id"]] = [str(list_1), stop_times[id]["stop_headsign"].lstrip()]
                    bus_dir[bus_num[1]] = stop_times[id]["stop_headsign"]

        else:
            bus_num = list(stop_times[id]["trip_id"].split("."))
            bus_num = list(bus_num[2].split("-"))
            if bus_num[1] in bus_dir:
                if bus_dir[bus_num[1]] == stop_times[id]["stop_headsign"]:
                    bus_dict[stop_times[id]["stop_id"]] = [[bus_num[1], stop_times[id]["stop_headsign"].lstrip()]]
                else:
                    bus_dict[stop_times[id]["stop_id"]] = [[bus_num[1], stop_times[id]["stop_headsign"].lstrip()]]
            else:
                bus_dir[bus_num[1]] = stop_times[id]["stop_headsign"]
                bus_dict[stop_times[id]["stop_id"]] = [[bus_num[1], stop_times[id]["stop_headsign"].lstrip()]]
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
        bus_num = list(stop_times[id]["trip_id"].split("."))
        bus_num = list(bus_num[2].split("-"))
        route_id = bus_num[1]
        route_id = route_id.strip("'")
        check = 0
        if route_id in bus_dict:
            for i in bus_dict[route_id]:
                if i == stop_times[id]["stop_headsign"].lstrip():
                    check = 1
            if check == 1:
                pass
            else:
                bus_dict[route_id].append(stop_times[id]["stop_headsign"].lstrip())
        else:
            bus_dict[route_id]=[stop_times[id]["stop_headsign"].lstrip()]
    return bus_dict
# main()
