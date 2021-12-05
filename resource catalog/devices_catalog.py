import json
from datetime import datetime
import time

"""
#it could be useless if a specific structure is not imposed.
class Device():
    def __init__(self,sensorID,endPoints,parameters,timestamp):
        self.sensorID=sensorID
        self.endPoints=endPoints
        self.parameters=parameters
        self.timestamp=timestamp
    
    def jsonify(self):
        device={'device_ID':self.sensorID,'end_points':self.endPoints,'parameters':self.parameters,'timestamp':self.timestamp}
        return device
"""
class DevicesCatalog():
    def __init__(self,devices_list):
        self.devices=devices_list

    def insertValue(self,device_ID,info):
        if not any(dev['bn']==device_ID for dev in self.devices):
            return self.addDevice(device_ID,info)
        else:
            return self.updateDevice(device_ID,info)
    
    def updateDevice(self,device_ID,info):
        for device in self.devices:
            if device['bn']==device_ID:
                for meas in info['e']:
                    if not any(p['n']==meas['n'] for p in device['e']):
                        device['e'].append(meas)
                    else:
                        for i in range(len(device['e'])):
                            if device['e'][i]['n']==meas['n']:
                                device['e'][i]=meas
                    device['last_update'],device['last_update_date']=self.last_update()
        return True
                
            
    def last_update(self):
        timestamp=time.time()
        date=datetime.now().strftime("%d/%m/%Y %H:%M")
        return timestamp,date

    def addDevice(self, device_ID, device_info):
        device_info['last_update'],device_info['last_update_date']=self.last_update()
        self.devices.append(device_info)
        return True
        
    def removeInactive(self,timeInactive):
        output=False
        for device in self.devices:
            device_ID=device['device_ID']
            if self.timestamp - device['timestamp']>timeInactive:
                self.devices.remove(device)
                #self.devices['last_update']=self.actualTime
                print(f'Device {device_ID} removed')
                output=True
        return output


    def removeDevice(self,device_ID):
        i=self.findPos(device_ID)
        if i is not False:
            self.devices.pop(i) 
            return True
        else:
            return i

    
