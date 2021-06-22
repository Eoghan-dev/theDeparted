import requests
import pyodbc
import  urllib.request, urllib.parse, urllib.error, json
import myPrivates

server = myPrivates.server
database = myPrivates.dbName
username = myPrivates.user
password = myPrivates.password
#open connection with sql server
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
# #making cursor easier to access
cursor = cnxn.cursor()

def get_current_bus():
    headers = {
        # Request headers
        'Cache-Control': 'no-cache',
        'x-api-key': '100d436970cb4ed5b1e954c64f541cb0',
    }

    params = urllib.parse.urlencode({
    })
    info_bus = ()
    try:

        gtfs = 'https://gtfsr.transportforireland.ie/v1/?format=json'
        r = requests.get(gtfs, params=params, headers=headers)
        data = json.loads(r.content)
        #print(data)
        for i in data["entity"]:
            id = i["id"]
            trip = i["trip_update"]["trip"]
            route_id = trip["route_id"]
            schedule = trip["schedule_relationship"]
            start_t = trip["start_time"]
            start_d = trip["start_date"]
            try:
                for j in i["trip_update"]["stop_time_update"]:
                    stop_id = j["stop_id"]
                    try:
                        test = j["departure"]
                        delay = test["delay"]
                    except:
                        try:
                            test = j["arrival"]
                            delay = test["delay"]
                        except:
                            delay = 0
                    info_bus = info_bus + ((id, route_id, schedule, start_t, start_d, stop_id,
                                            delay),)
            except:
                stop_id = None
                delay = None
                info_bus = info_bus + ((id, route_id, schedule, start_t, start_d, stop_id,
                                            delay),)
        print(len(info_bus))
        write_current_bus(info_bus)
        print("finished")


    except Exception as e:
        print(e)

def write_current_bus(x):
    current_bus = "INSERT INTO dublin_bus_current_info (id, route_id, " \
                    "schedule , start_t, start_d, stop_id, delay) " \
                    "VALUES (?, ?, ?, ?, ?, ?, ?)"

    cursor.execute(" SELECT count(*) FROM information_schema.tables WHERE table_name = 'dublin_bus_current_info'")

    # Creates table for historical bus info
    if (cursor.fetchone()[0] == 0):
        cursor.execute("CREATE TABLE dublin_bus_current_info ( id VARCHAR(40), "
                         "route_id VARCHAR(40), schedule VARCHAR(40), "
                         "start_t VARCHAR(20), start_d VARCHAR(20), stop_id VARCHAR(20), "
                         "delay INT) ")
    cursor.execute("truncate table dublin_bus_current_info;")
    cursor.executemany(current_bus, x)
    cnxn.commit()
get_current_bus()