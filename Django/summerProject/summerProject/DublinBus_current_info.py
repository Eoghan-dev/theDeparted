import requests
from zipfile import ZipFile
import json
import os

def main():
    download()
    files = ['routes.txt','shapes.txt','stop_times.txt','stops.txt']
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
       zipObj.extractall(path='../../summerProject/dublinBus/static/dublinBus/Dublin_bus_info')
    print('Download Completed!!!')
    os.remove(filename)

def json_convertor(filename):
    # resultant dictionary
    dict1 = {}
    with open('../../summerProject/dublinBus/static//dublinBus/Dublin_bus_info/'+filename, encoding="utf-8-sig") as fh:
        # count variable for id
        l = 1

        for line in fh:
            if (l==1):
                #Comma present in stops.txt for stop name that seperates name with number
                if filename == "stops.txt":
                    ext_line = "stop_id, stop_name, stop_num, stop_lat, stop_lon"
                    fields = list(ext_line.strip().split(','))
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
                        elif i>2:
                            dict2[fields[i]] = description[i-1]
                        else:
                            dict2[fields[i]] = description[i]
                    else:
                        dict2[fields[i]] = description[i]
                    i = i + 1
                # appending the record of each id
                dict1[id] = dict2
            l = l + 1
    # creating json file
    filename = filename.strip('.txt')
    out_file = open("../../summerProject/dublinBus/static/dublinBus/Dublin_bus_info/json_files/"+filename+".json", "w")
    json.dump(dict1, out_file, indent=4)
    out_file.close()
    print("Finished saving", filename + ".json")

main()