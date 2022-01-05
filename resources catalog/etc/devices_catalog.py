import json
from datetime import datetime
import time

#it could be useless if a specific structure is not imposed.
class Device():
    def __init__(self,deviceID,endpoints,info):
        self._deviceID=deviceID
        self.endpoints=endpoints
        self.info=info
        self.timestamp=time.time()
        self.date=datetime.now().strftime("%d/%m/%Y %H:%M")
    
    def jsonify(self):
        device={'deviceID':self._deviceID,'endpoints':self.endpoints,'resources':self.info,'timestamp':self.timestamp,'date':self.date}
        return device

class DevicesCatalog():
    def __init__(self,devices_list):
        self.devices=devices_list

    def insertValue(self,device_ID,info):
        if not any(dev['deviceID']==device_ID for dev in self.devices):
            return self.addDevice(device_ID,info)
        else:
            return self.updateDevice(device_ID,info)
    
    def updateDevice(self,device_ID,info):
        for device in self.devices:
            if device['deviceID']==device_ID:
                timestamp=time.time()
                date=datetime.now().strftime("%d/%m/%Y %H:%M")
                device['resources']=info['e']
                device['timestamp']=timestamp
                device['date']=date
                print("Device {} updated.\n".format(device_ID))
                return True


    def addDevice(self, device_ID, device_info):
        try:
            device=Device(device_ID,device_info['endpoints'],device_info['e']).jsonify()
            #print(device)
            self.devices.append(device)
            
            print("New device {} added.\n".format(device_ID))
            return True
        except Exception as e:
            print(e)
            print("New device {} can't be added.\n".format(device_ID))
            return False
        
    def removeInactive(self,timeInactive):
        removed_devices=[]
        for device in self.devices:
            device_ID=device['deviceID']
            if time.time() - device['timestamp']>timeInactive:
                self.devices.remove(device)
                #self.devices['last_update']=self.actualTime
                print(f'Device {device_ID} removed')
                removed_devices.append(device_ID)
        return removed_devices

    def findPos(self,device_ID):
        notFound=1
        for i in range(len(self.devices)):
            if self.devices[i]['deviceID']==device_ID:
                notFound=0
                return i
        if notFound==1:
            return False
        
    def removeDevice(self,device_ID):
        i=self.findPos(device_ID)
        if i is not False:
            self.devices.pop(i) 
            return True
        else:
            return i

    
