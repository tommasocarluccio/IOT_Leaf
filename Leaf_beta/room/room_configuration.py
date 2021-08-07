import json
import requests
import sys
from lcd import LCDAdapter

if __name__ == '__main__':
    configuration_filename=sys.argv[1]
    myRoom=LCDAdapter(configuration_filename)
    myRoom.DisplayReset()
    print("%% Connecting to Catalog %%")
    putBody={'roomID':myRoom.roomID,'roomName':myRoom.roomName,'thingSpeakURL':myRoom.thingSpeakURL}
    
    try:
        r=requests.put(myRoom.catalogURL+'/insertRoom', json=putBody)
        if r.status_code==200:
            myRoom.configurationLed(True)
            output="{} - Connection performed".format(myRoom.roomID)
            print(output)
        else:
            myRoom.configurationLed(False)
            print("Catalog connection failed: Room not inserted\n")
    except:
        myRoom.errorPrinting()
        print("No Catalogue connection available.\n")
        
