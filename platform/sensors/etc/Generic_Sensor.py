from etc.simplePublisher import *
import time
import json
    
class SensorPublisher(MyPublisher):
    def __init__(self, configuration_filename, platform_ID,room_ID, device_ID,broker_ip,broker_port,data_topic):
        self.alive=True
        self.connected=False
        self.broker_IP=broker_ip
        self.broker_port=broker_port
        self.platform_ID=platform_ID
        self.room_ID=room_ID
        self.settings=json.load(open(configuration_filename,"r"))
        self.time_sleep=self.settings['time_sleep']
        self.device_ID=device_ID
        self.topic=data_topic+'/'.join([self.platform_ID,self.room_ID,self.device_ID])
        MyPublisher.__init__(self,self.platform_ID+'_'+self.room_ID+'_'+self.device_ID+"_publisher",self.broker_IP,self.broker_port)
        
    def publishData(self,result_list):
        e=[]
        for result in  result_list:
            for element in self.settings['parameters']:
                if element['parameter']==result['parameter']:
                    e.append({"n":result["parameter"],"u":element["unit"],"t":result["time"],"v":result["value"]})
                    data={"bn":self.platform_ID+'/'+self.room_ID+'/'+self.device_ID,"e":e}
                    print(element['parameter']+": "+str(result['value'])+' '+ element['unit'])
        topic=self.topic
        self.myPublish(topic,json.dumps(data))
                               
    def create_info(self):
        e=[]
        for element in self.settings['parameters']:
            resource={"n":element["parameter"],"u":element["unit"],"topic":self.topic}
            e.append(resource)
        self._data={"bn":self.device_ID,"endpoints":self.settings['end_points'],"e":e}
        
        
            
        
                    
