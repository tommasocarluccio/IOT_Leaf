from simplePublisher import *
import time
import json
from datetime import datetime
import requests

class Sensor(object):
    def __init__(self, configuration_filename,room_filename):
        self.configuration=json.load(open(configuration_filename))
        self.roomConfiguration=json.load(open('../'+room_filename))
        self.roomID=self.roomConfiguration['roomID']
        self.sensorID=self.configuration['sensorID']
        self.parameters=self.configuration.get('parameters')
        self.catalogURL=self.roomConfiguration['catalog']
    
class SensorPublisher(MyPublisher,Sensor):
    def __init__(self, configuration_filename,room_filename):
        Sensor.__init__(self,configuration_filename,room_filename)
        clientID=requests.get(self.catalogURL+'/'+'clientID')
        self.clientID=clientID.json()
        self.topic='/'.join([self.clientID,self.sensorID])
        broker=requests.get(self.catalogURL+'/'+'broker')
        self.broker=broker.json()[0].get('addressIP')
        brokerPort=requests.get(self.catalogURL+'/'+'broker')
        self.brokerPort=brokerPort.json()[0].get('port')
        MyPublisher.__init__(self,self.clientID,self.topic,self.broker,self.brokerPort)       
        self.message=[]
        for parameter in self.parameters:
            message={'Client ID': self.clientID, 'Sensor': self.sensorID, 'parameter':parameter.get('parameter'), 'value': None,'time':'','timestamp':'','unit':parameter.get('unit')}
            self.message.append(message)
            
    def updateRoom(self):
        roomsList=requests.get(self.catalogURL+'/'+'roomsList').json()
        notFound=1
        for room in roomsList:
            if str(room)==str(self.roomID):
                notFound=0
        if notFound==1:
            requests.put(self.catalogURL+'/'+'insertRoom', data=json.dumps(self.configuration))
            
    def PublishData(self,mylist):
        now=datetime.now()
        dt_string=now.strftime("%H:%M")
        actualTime=time.time()
        for message in self.message:
            for result in mylist:
                if message['parameter']==result['parameter'] and result['value'] is not None:
                    message['value']=result['value']
                    message['time']=dt_string
                    message['timestamp']=actualTime
                    topic=self.topic+'/'+message['parameter']
                    self.myPublish(topic,json.dumps(message))
                    print (result['value'])
                    
    def pingCatalog(self):
        try: 
            requests.put(self.catalogURL+'/'+'insertDevice'+'?room='+self.roomID, data=json.dumps(self.configuration))
        except:
            print("No catalog found")
