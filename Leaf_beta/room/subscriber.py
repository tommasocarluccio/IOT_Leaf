import json
import requests
import time
from MyMQTT import *
import sys

class DataCollector():
    def __init__(self,room_filename):
        configuration=json.load(open(room_filename))
        self.catalogURL=configuration['catalog']
        self.roomID=configuration['roomID']
        clientID=requests.get(self.catalogURL+'/'+'clientID')
        broker=requests.get(self.catalogURL+'/'+'broker')
        self.broker=broker.json()[0].get('addressIP')
        self.brokerPort=broker.json()[0].get('port')
        self.clientID=clientID.json()
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
            r=requests.put(self.catalogURL+'/insertValue', json=putBody)
            print(f'At {self.clientID} ({t})\n{parameter}: {value}\n')
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



