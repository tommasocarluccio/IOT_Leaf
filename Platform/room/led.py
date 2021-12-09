import sys
import json
import requests
import time
import RPi.GPIO as GPIO
from etc.MyMQTT import *

class LED():
    def __init__(self,clientID,broker_IP,broker_port,pin):
        self.broker_IP=broker_IP
        self.broker_port=broker_port
        self.clientID=clientID
        self.pin=int(pin)
        self.client=MyMQTT(self.clientID,self.broker_IP,self.broker_port,self)
    def run(self):
        self.client.start()
        print('{} has started'.format(self.clientID))
    def end(self):
        self.client.stop()
        print('{} has stopped'.format(self.clientID))
    def follow(self,topic):
        self.client.mySubscribe(topic)
    def unfollow(self,topic):
        self.client.unsubscribe(topic)
    def notify(self,topic,msg):
        payload=json.loads(msg)
        print(payload)
        if payload:
            GPIO.output(self.pin,GPIO.HIGH)
        else:
            GPIO.output(self.pin,GPIO.LOW)
            
if __name__=='__main__':
    filename=sys.argv[1]
    pin=sys.argv[2]
    mqtt_flag=False
    
    roomContent=json.load(open(filename,"r"))
    room_ID=roomContent['room_info']['room_ID']
    platform_ID=roomContent['platform_ID']
    serviceCatalogAddress=roomContent['service_catalog']
        
    while not mqtt_flag:
        try:
            broker=requests.get(serviceCatalogAddress+'/broker').json()
            broker_IP=broker.get('IP_address')
            broker_port=broker.get('port')
            data_topic=broker['topic'].get('data')
            myLED=LED("LED",broker_IP,broker_port,pin)
            myLED.run()
            mqtt_flag=True
        except Exception as e:
            print("Can't connect to mqtt broker. New attempt...")
            print(e)
            time.sleep(30)
            
    time.sleep(1)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(myLED.pin,GPIO.OUT)
    myLED.follow(data_topic+platform_ID+"/"+room_ID+"/LED")
    while True:
        time.sleep(1)
    myOLED.stop()

