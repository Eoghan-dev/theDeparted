import requests
from zipfile import ZipFile
import json

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
       zipObj.extractall(path='Dublin_bus_info')
    print('Download Completed!!!')

def json_convertor(filename):
    # resultant dictionary
    dict1 = {}
    with open('Dublin_bus_info/'+filename, encoding="utf8") as fh:
        # count variable for id
        l = 1

        for line in fh:
            if (l==1):
                fields = list(line.strip().split(','))
            if (l!=1):
                # reading line by line from the text file
                description = list(line.strip('"').split(','))
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
                    dict2[fields[i]] = description[i]
                    i = i + 1
                # appending the record of each id
                dict1[id] = dict2
            l = l + 1
    # creating json file
    filename = filename.strip('.txt')
    out_file = open("Dublin_bus_info/json_files/"+filename+".json", "w")
    json.dump(dict1, out_file, indent=4)
    out_file.close()
    print("Finished saving", filename + ".json")

main()