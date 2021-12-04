import json
import requests
import time
from conf.MyMQTT import *
from conf.room_config_Class import RoomConfig
import sys

class DataCollector():
    def __init__(self,room_filename):
        RoomConfig.__init__(self,room_filename)
        RoomConfig.retrieveInfo(self)
        self.client=MyMQTT(self.clientID,self.broker,self.brokerPort,self)
    def run(self):
        self.client.start()
        print('{} has started'.format(self.clientID))
    def end(self):
        self.client.stop()
        print('{} has stopped'.format(self.clientID))
    def follow(self,topic):
        self.client.mySubscribe(topic)
    def notify(self,topic,msg):
        payload=json.loads(msg)
        sensorID=payload['Sensor']
        value=(payload['value'])
        parameter=payload['parameter']
        timestamp=payload['timestamp']
        t=payload['time']
        putBody={'roomID':self.roomID,'sensorID':sensorID,'parameter':parameter,'value':str(value)}
        try:
            r=requests.put(self.serverURL+'/insertValue/'+self.catalogID, json=putBody)
            print(f'At {self.roomID} ({t})\n{parameter}: {value}\n')
        except:
            print("Error detected")

if __name__ == '__main__':
    room_filename=sys.argv[1]
    collection=DataCollector(room_filename)
    collection.run()
    
    while True:
        collection.follow(collection.clientID+'/#')
        time.sleep(3)
        collection.client.unsubscribe()
        time.sleep(1)
    collection.end()



