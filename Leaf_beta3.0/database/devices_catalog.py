import json
from datetime import datetime
import time
from devices import *

class DevicesCatalog():
    def __init__(self,myRoom):
        self.myRoom=myRoom
        self.actualTime=time.time()
        self.now=datetime.now()
        self.timestamp=self.now.strftime("%d/%m/%Y %H:%M")
        
    def retrieveAllDevices(self):
        devices=self.myRoom.get('devices')
        return devices
    
    def retrieveDeviceID(self,sensorID):
        notFound=1
        for device in self.myRoom.get('devices'):
            if str(device['sensorID']) ==sensorID:
                notFound=0
                return device
        if notFound==1:
            return False

    def retrieveValue(self,sensorID,parameter):
        device=self.retrieveDeviceID(sensorID)
        if device is not False:
            notFound=1
            for resource in device.get('parameters'):
                if resource['parameter']==parameter:
                    notFound=0
                    return resource
            if notFound==1:
                return False
        else:
            return False
        
    def insertValue(self,sensorID,parameter,value):
        resource=self.retrieveValue(sensorID,parameter)
        if resource is not False:
            resource['value']=value
            output='\nInserted: '+parameter+' '+value+' '+resource['unit']+'\n'
            return output       

    def insertDevice(self, sensorID, endPoints, availableResources):
        device=self.retrieveDeviceID(sensorID)
        if device is not False:
            #update the device if it exists
            device['end_points']=endPoints
            device['timestamp']=self.actualTime
            output=False
        else:
            #otherwise create the device
            newDevice=Device(sensorID,endPoints,availableResources,self.actualTime).jsonify()
            self.myRoom.get('devices').append(newDevice)
            output=True
        return output
        
    def removeInactive(self,timeInactive):
        for device in self.myRoom.get('devices'):
            sensorID=device['sensorID']
            if self.actualTime - device['timestamp']>timeInactive:
                self.myRoom.get('devices').remove(device)
                self.myRoom['last_update']=self.timestamp
                print(f'Devices {sensorID} removed')
    
    def removeDevice(self,sensorID):
        device=self.retrieveDeviceID(sensorID)
        if device is not False:
            self.myRoom.get('devices').remove(device)
            self.myRoom['last_update']=self.timestamp
            return True
        else:
            return False

    