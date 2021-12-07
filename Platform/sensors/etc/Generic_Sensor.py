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
            broker=self.retrieve_service("broker")
            self.broker_IP=broker.get('IP_address')
            self.broker_port=broker.get('port')
            self.setup(self.broker_IP,self.broker_port)
            return True
        except Exception as e:
            print(e)
            return False

    def retrieve_service(self,service):
        r=requests.get(self.serviceCatalogAddress+'/'+service).json()
        return r
        
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
                    
    def create_info(self):
        for element in self.settings['parameters']:
            e=[{"n":element["parameter"],"u":element["unit"],"topic":self.topic+"/"+element['parameter']}]
        data={"bn":self.device_ID,"endpoints":self.settings['end_points'],"e":e}
        return data
    
    def pingCatalog(self,data):
        try:
            catalog=self.retrieve_service("resource_catalog")['url']
            r=requests.put("{}/insertDevice/{}/{}".format(catalog,self.platform_ID,self.room_ID),data=json.dumps(data))
            if r.status_code==200:
                return True
            else:
                return False
        except Exception as e:
            print(e)
                    
