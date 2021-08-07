import json
import requests
import time
from MyMQTT import *

class DataCollector():
    def __init__(self):
        self.catalogURL='http://127.0.0.1:8080/catalog'
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
        value=(payload['value'])
        parameter=payload['parameter']
        timestamp=payload['timestamp']
        t=payload['time']
        putBody={'value':str(value)}
        r=requests.put('http://127.0.0.1:8081'+'/'+parameter, json=putBody)
        
        #params={'field3':temp}
        #url='https://api.thingspeak.com/update?api_key=1G5BT51PIND6DGZY'
        #r=requests.post(url,params=params)
        #print(r.status_code)
        
        
        print(f'At {self.clientID} ({t})\n{parameter}: {value}\n')

        

if __name__ == '__main__':
    collection=DataCollector()
    collection.run()
    
    while True:
        deviceList=requests.get('http://127.0.0.1:8080/catalog'+'/'+'devices').json()
        for device in deviceList:
            sensorID=device['sensorID']
            
            for parameter in device['parameters']:
                collection.follow(collection.clientID+'/'+sensorID+'/'+parameter.get('parameter')+'/#')
                time.sleep(5)
                collection.client.unsubscribe()
        time.sleep(1)
    collection.end()



