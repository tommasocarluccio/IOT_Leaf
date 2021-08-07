import json
import requests
import sys
import time
from lcd import LCDAdapter

if __name__ == '__main__':
    configuration_filename=sys.argv[1]
    catalogID=sys.argv[2]
    myRoom=LCDAdapter(configuration_filename)
    myRoom.DisplayReset()
    print("%% Connecting to Catalog %%")
    putBody={'roomID':myRoom.roomID,'roomName':myRoom.roomName,'thingSpeakURL':myRoom.thingSpeakURL,'devices':myRoom.devices}
    configuration=json.load(open(configuration_filename))
    configuration['catalogID']=catalogID
    try:
        r=requests.put(myRoom.serverURL+'/insertRoom''/'+catalogID, json=putBody)
        if r.status_code==200:
            myRoom.configurationLed(True)
            output="{} - Connection performed".format(myRoom.roomID)
            with open(configuration_filename,'w') as file:
                json.dump(configuration,file, indent=4)
            print(output)
            
        else:
            myRoom.configurationLed(False)
            print("Catalog connection failed: Room not inserted\n")
    except:
        myRoom.errorPrinting()
        print("No Catalogue connection available.\n")     
    myRoom.DisplayReset()
