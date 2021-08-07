from conf.room_config_Class import RoomConfig
import requests
import time
import json

class Adapter(RoomConfig):
    def __init__(self,room_filename):
        RoomConfig.__init__(self,room_filename)
        print("\n%% LEAF %%\n")
        print("Connected to "+self.thingSpeakURL)
        print("Standard resources are: "+ " ".join(x for x in self.standardParameters)+"\n")
        
    def findDevices(self):
        stringURL=self.basicURL+'/rooms/'+self.roomID+'/devices'
        self.devices=requests.get(stringURL).json()
    
    def identifySensor(self,parameter):
        for dev in self.devices:
            for par in dev['parameters']:
                if par['parameter']==parameter:
                    output="{}\n{} is used for {}".format(self.roomID,dev['sensorID'],parameter)
                    #print(output)
                    return dev['sensorID']
                
    def retrieveData(self,sensorID,parameter):
        self.parameter=parameter
        try:
            stringURL=self.basicURL+'/rooms/'+self.roomID+'/devices/'+sensorID+'?parameter='+parameter
            result=requests.get(stringURL).json()
            self.value=int(float(result['value']))
            return self.value
        except:
            return None
        
    def sendThingSpeak(self,temperature,humidity,AQI):
        self.message['Temperature']=(temperature)
        self.message['Humidity']=(humidity)   
        self.message['AQI']=(AQI)

        params={'field2':self.message['Temperature'],'field3': self.message['Humidity'],'field1':self.message['AQI']}
        url=self.thingSpeakURL
        try:
            r=requests.post(url,params=params)
            return self.message
        except:
            return "ThingSpeak unreachable"