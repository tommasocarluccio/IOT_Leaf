from conf.simplePublisher import *
import sys
sys.path.append('/home/pi/Desktop/Leaf/Leaf_beta_v2/room/conf')
from room_config_Class import RoomConfig
import time
import json
from datetime import datetime
import requests

class Sensor(RoomConfig):
    def __init__(self, configuration_filename,room_filename):
        RoomConfig.__init__(self,'../conf/etc/'+room_filename)
        RoomConfig.retrieveInfo(self)
        self.configuration=json.load(open(configuration_filename))
        self.sensorID=self.configuration['sensorID']
        self.parameters=self.configuration.get('parameters')
    
class SensorPublisher(MyPublisher,Sensor):
    def __init__(self, configuration_filename,room_filename):
        Sensor.__init__(self,configuration_filename,room_filename)
        self.topic='/'.join([self.clientID,self.sensorID])
        MyPublisher.__init__(self,self.clientID,self.topic,self.broker,self.brokerPort)       
        self.message=[]
        for parameter in self.parameters:
            message={'Client ID': self.clientID, 'Sensor': self.sensorID, 'parameter':parameter.get('parameter'), 'value': None,'time':'','timestamp':'','unit':parameter.get('unit')}
            self.message.append(message)
            
    def updateRoom(self):
        roomsList=requests.get(self.serverURL+'roomsList').json()
        notFound=1
        for room in roomsList:
            if str(room)==str(self.roomID):
                notFound=0
        if notFound==1:
            requests.put(self.serverURL+'insertRoom', data=json.dumps(self.configuration))
            
    def PublishData(self,mylist):
        now=datetime.now()
        dt_string=now.strftime("%H:%M")
        actualTime=time.time()
        for message in self.message:
            for result in mylist:
                if message['parameter']==result['parameter'] and result['value'] is not None and result['value']>=0:
                    message['value']=result['value']
                    message['time']=dt_string
                    message['timestamp']=actualTime
                    topic=self.topic+'/'+message['parameter']
                    self.myPublish(topic,json.dumps(message))
                    print (result['value'])
                    
    def pingCatalog(self):
        try:
            requests.put(self.serverURL+'insertDevice/'+self.catalogID+'?room='+self.roomID, data=json.dumps(self.configuration))
        except:
            print("No catalog found")
