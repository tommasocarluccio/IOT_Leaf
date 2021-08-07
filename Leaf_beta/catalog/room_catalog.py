import json
from datetime import datetime
import time
from devices import *

class RoomCatalog:
    def __init__(self,myCatalog,catalogFileName):
        self.myCatalog=myCatalog
        self.myRooms = self.myCatalog['rooms']
        self.catalogFileName=catalogFileName
        self.lastUpdate=myCatalog['last_update']
        
    def retrieveAllDevices(self,roomID):
        self.data={x['roomID']: x for x in self.myRooms}
        try:
            devices=json.dumps(self.data[roomID].get('devices'),indent=4)
            return devices
        except:
            return "Room not found"
    
    def retrieveDeviceID(self, roomID, sensorID):
        self.data={x['roomID']: x for x in self.myRooms}
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
        self.data={x['roomID']: x for x in self.myRooms}
        notFound=1
        for device in self.data[roomID].get('devices'):
            if device['sensorID']==sensorID:
                for resource in device.get('parameters'):
                    if resource['parameter']==parameter:
                        notFound=0
                        return json.dumps(resource,indent=4)
        if notFound==1:
            return False
        
    def insertValue(self,roomID,sensorID,parameter,value):
        self.data={x['roomID']: x for x in self.myRooms}
        for device in self.data[roomID].get('devices'):
            if device['sensorID']==sensorID:
                for resource in device.get('parameters'):
                    if resource['parameter']==parameter:
                        resource['value']=value
                        output='\nInserted: '+parameter+' '+value+' '+resource['unit']+'\n'
                        return output
        self.save(self.catalogFileName)
        
            

    def insertDevice(self,roomID, sensorID, endPoints, availableResources):
        self.data={x['roomID']: x for x in self.myRooms}
        notFound=1
        timestamp=time.time()
        
        for dev in self.data[roomID].get('devices'):
            if dev['sensorID'] == sensorID:
                notFound=0
                dev['end_points']=endPoints
                #dev['parameters']=availableResources
                dev['timestamp']=timestamp
                output=False
                
        if notFound!=0:
            newDevice=Device(sensorID,endPoints,availableResources,timestamp).jsonify()
            self.data[roomID].get('devices').append(newDevice)
            #print(newDevice)
            output=True
        now=datetime.now()
        lastUpdate=now.strftime("%d/%m/%Y %H:%M")
        self.dateRoomUpload(roomID,lastUpdate)
        self.save(self.catalogFileName)
        #print(self.data[roomID])
        return output
        
    def dateRoomUpload(self,roomID,dt_string):
        self.data={x['roomID']: x for x in self.myRooms}
        self.data[roomID]['last_update']=dt_string

    def save(self,catalogFileName):
        with open(catalogFileName,'w') as file:
            json.dump(self.myCatalog,file, indent=4)

    def removeInactive(self,roomID,timeInactive):
        self.data={x['roomID']: x for x in self.myRooms}
        self.actualTime=time.time()
        for device in self.data[roomID].get('devices'):
            sensorID=device['sensorID']
            if self.actualTime - device['timestamp']>timeInactive:
                self.data[roomID].get('devices').remove(device)
                print(f'Devices {sensorID} removed')
        self.save(self.catalogFileName) 

    
    def removeDevice(self,roomID, deviceID):
        self.data={x['roomID']: x for x in self.myRooms}
        #myList=[item for item in self.data[roomID].get('devices') if item['sensorID']!=deviceID]
        for device in self.data[roomID].get('devices'):
            if device['sensorID']==deviceID:
                self.data[roomID].get('devices').remove(device)
                self.save(self.catalogFileName)
                return True
        

    
