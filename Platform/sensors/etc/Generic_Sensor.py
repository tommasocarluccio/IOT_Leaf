from etc.simplePublisher import *
import sys
import time
import json
from datetime import datetime
import requests
    
class SensorPublisher(MyPublisher):
    def __init__(self, configuration_filename, device_ID):
        self.roomContent=json.load(open("../room/conf/room_settings.json","r"))
        self.settings=json.load(open(configuration_filename,"r"))
        self.time_sleep=self.settings['time_sleep']
        self.room_ID=self.roomContent['room_info']['room_ID']
        self.platform_ID=self.roomContent['platform_ID']
        self.device_ID=device_ID
        self.serviceCatalogAddress=self.roomContent['service_catalog']
        self.topic='/'.join([self.platform_ID,self.room_ID,self.device_ID])
        MyPublisher.__init__(self,self.platform_ID+'_'+self.room_ID+'_'+self.device_ID+"_publisher")
    
    def load(self):
        try:
            self.broker_IP,self.broker_port=self.retrieve_service("broker")
            self.setup(self.broker_IP,self.broker_port)
            return True
        except Exception as e:
            print(e)
            return False
        
    def retrieve_service(self,service):
        broker=requests.get(self.serviceCatalogAddress+'/broker').json()
        broker_IP=broker.get('IP_address')
        broker_port=broker.get('port')
        return broker_IP,broker_port
        
    def publishData(self,result_list):
        for result in  result_list:
            for element in self.settings['parameters']:
                if element['parameter']==result['parameter']:
                    e=[{"n":result["parameter"],"u":element["unit"],"t":result["time"],"v":result["value"]}]
                    data={"bn":self.platform_ID+'/'+self.room_ID+'/'+self.device_ID,"e":e}
                    #data={"bn":self.device_ID,"e":e}
                    topic=self.topic+'/'+element['parameter']
                    #print(topic)
                    self.myPublish(topic,json.dumps(data))
                    print (str(result['value'])+' '+ element['unit'])
                    
