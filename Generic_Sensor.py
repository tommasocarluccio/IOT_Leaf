from MyMQTT import *
from simplePublisher import *
import time
import json
from datetime import datetime
import serial

class Sensor(object):
    def __init__(self, configuration_filename):
        self.configuration=json.load(open(configuration_filename))
        self.sensorID=self.configuration['sensorID']
        self.parameters=self.configuration.get('parameters')
        
class SensorPublisher(MyPublisher,Sensor):
    def __init__(self, configuration_filename, catalog_filename):
        Sensor.__init__(self,configuration_filename)
        self.settings=json.load(open(catalog_filename))
        self.clientID=self.settings['clientID']
        self.topic='/'.join([self.clientID,self.sensorID])
        self.broker=self.settings["broker"]
        print(self.clientID)
        MyPublisher.__init__(self,self.clientID,self.topic,self.broker)       
        self.message=[]
        for parameter in self.parameters:
            message={'Client ID': self.clientID, 'Sensor': self.sensorID, 'parameter':parameter.get('parameter'), 'value': 0,'time':'','timestamp':'','unit':parameter.get('unit')}
            self.message.append(message)

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
                    print (message)   

