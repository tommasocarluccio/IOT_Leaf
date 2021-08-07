import json
from datetime import datetime
import time
from devices import *

class RoomCatalog:
    def __init__(self,myCatalog,catalogFileName):
        self.myCatalog=myCatalog
        self.myRooms = self.myCatalog['rooms']
        self.catalogFileName=catalogFileName
        self.data={x['roomID']: x for x in self.myRooms}
        
    def retrieveAllDevices(self,roomID):
        try:
            devices=json.dumps(self.data[roomID].get('devices'),indent=4)
            return devices
        except:
            return "Room not found"
    
    def retrieveDeviceID(self, roomID, sensorID):
        try:
            notFound=1
            for dev in self.data[roomID].get('devices'):
                if str(dev['sensorID']) ==sensorID:
                    notFound=0
                    device= json.dumps(dev,indent=4)
                    return device
            if notFound==1:
                return "Device not found"
        except:
            return "Room not found"

    def retrieveValue(self,roomID,sensorID,parameter):
        notFound=1
        for device in self.data[roomID].get('devices'):
            if device['sensorID']==sensorID:
                for resource in device.get('parameters'):
                    if resource['parameter']==parameter:
                        notFound=0
                        return json.dumps(resource,indent=4)
        if notFound==1:
            return False

    def insertDevice(self,roomID, sensorID, endPoints, availableResources):
        notFound=1
        timestamp=time.time()
        
        for dev in self.data[roomID].get('devices'):
            if dev['sensorID'] == sensorID:
                notFound=0
                dev['end_points']=endPoints
                dev['parameters']=availableResources
                dev['timestamp']=timestamp
                
        if notFound!=0:
            newDevice=Device(sensorID,endPoints,availableResources,timestamp).jsonify()
            self.data[roomID].get('devices').append(newDevice)
            print(newDevice)
        now=datetime.now()
        lastUpdate=now.strftime("%d/%m/%Y %H:%M")
        self.dateRoomUpload(roomID,lastUpdate)
        self.save(self.catalogFileName)
        print(self.data[roomID])
        return "Successful procedure"
        
    def dateRoomUpload(self,roomID,dt_string):
        self.data[roomID]['last_update']=dt_string

    def save(self,catalogFileName):
        with open(catalogFileName,'w') as file:
                    json.dump(self.myCatalog,file, indent=4)

    def removeInactive(self,roomID,timeInactive):
        self.actualTime=time.time()
        for device in self.data[roomID].get('devices'):
            sensorID=device['sensorID']
            if self.actualTime - device['timestamp']>timeInactive:
                self.data[roomID].get('devices').remove(device)
                print(f'Devices {sensorID} removed')
        self.save(self.catalogFileName) 

    
    def removeDevice(self,roomID, deviceID):
        #myList=[item for item in self.data[roomID].get('devices') if item['sensorID']!=deviceID]
        for device in self.data[roomID].get('devices'):
            if device['sensorID']==deviceID:
                self.data[roomID].get('devices').remove(device)
                self.save(self.catalogFileName)
                return True
        

    
