import pyodbc
import myPrivates

server = myPrivates.server
database = myPrivates.dbName
username = myPrivates.user
password = myPrivates.password
#open connection with sql server
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
# #making cursor easier to access
cursor = cnxn.cursor()

def get_bus_stop():
    f = open("stops.txt", "r")
    count = 0
    entries = ()
    while (True):
        try:
            # read next line
            line = f.readline()
            # if line is empty, you are done with all lines in the file
            if not line:
                break
            x = line.split('","')
            y = x[1].split(", stop ")
            stop_id=x[0]
            stop_name=y[0]
            stop_number=y[1]
            stop_lat=x[2]
            stop_lon=x[3]
            entries += ((stop_id, stop_name, stop_number, stop_lat,
                         stop_lon),)
        except Exception as e:
            print(e)
            count +=1
            print("oh no")
    # close file
    f.close
    write_dublin_bus_stops(entries)
    print("Number of stations failing:",count)

def write_dublin_bus_stops(x):
    bus_stops = "INSERT INTO dublin_bus_stops (stop_id, stop_name, " \
                    "stop_number , stop_lat, stop_lon) " \
                    "VALUES (?, ?, ?, ?, ?)"

    cursor.execute(" SELECT count(*) FROM information_schema.tables WHERE table_name = 'dublin_bus_stops'")
    # Creates table for bus stop info
    if (cursor.fetchone()[0] == 0):
        cursor.execute("CREATE TABLE dublin_bus_stops ( stop_id VARCHAR(40), "
                         "stop_name VARCHAR(40), stop_number VARCHAR(40), "
                         "stop_lat VARCHAR(20), stop_lon VARCHAR(20)) ")
    cursor.execute("truncate table dublin_bus_current_info;")
    cursor.executemany(bus_stops, x)
    cnxn.commit()
get_bus_stop()