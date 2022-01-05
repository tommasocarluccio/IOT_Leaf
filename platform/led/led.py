import sys
import json
import requests
import threading
import time
import RPi.GPIO as GPIO
from etc.MyMQTT import *

class pingThread(threading.Thread):
    def __init__(self,threadID,platform_ID,room_ID,data,catalog_url):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.platform_ID=platform_ID
        self.room_ID=room_ID
        self.data=data
        self.connection_flag=False
        self.serviceCatalogAddress=catalog_url
        
    def run(self):
        while True:
            print("Pinging the Catalog...")
            while self.pingCatalog() is False:
                print("Failed. New attempt...")
                time.sleep(10)
            print("Device has been registered/updated on Catalog")
            self.connection_flag=True
            time.sleep(60)
    
    
    def pingCatalog(self):
        try:
            catalog=requests.get(self.serviceCatalogAddress+'/resource_catalog').json()['url']
            r=requests.put("{}/insertDevice/{}/{}".format(catalog,self.platform_ID,self.room_ID),data=json.dumps(self.data))
            if r.status_code==200:
                return True
            else:
                return False
        except Exception as e:
            #print(e)
            return False
        
class ReceiveCommandThread(threading.Thread):
    def __init__(self,threadID,sensor):
        threading.Thread.__init__(self)
        self.sensor=sensor
        
    def run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.sensor.pin,GPIO.OUT)
        self.sensor.follow(self.sensor.topic)
        while True:
            time.sleep(1)
        self.sensor.end()

class LED():
    def __init__(self,clientID,base_topic,broker_IP,broker_port,parameter,pin):
        self.broker_IP=broker_IP
        self.broker_port=broker_port
        self.clientID=clientID+"_"+parameter
        self.pin=int(pin)
        self.parameter=parameter
        self.topic=base_topic+"/"+self.clientID
    
    def create_info(self):
        e=[]
        resource={"n":self.parameter+"_warning","u":None,"topic":self.topic}
        e.append(resource)
        self._data={"bn":self.clientID,"endpoints":"MQTT","e":e}
    
    def setup(self):
        print("Connecting...")
        self.create_info()
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
        if payload:
            GPIO.output(self.pin,GPIO.HIGH)
            print("LED is on")
        else:
            GPIO.output(self.pin,GPIO.LOW)
            
if __name__=='__main__':
    filename=sys.argv[1]
    platform_ID=sys.argv[2]
    room_ID=sys.argv[3]
    pin=sys.argv[4]
    mqtt_flag=False
    
    file_content=json.load(open(filename,"r"))
    serviceCatalogAddress=file_content['service_catalog']
    clientID=file_content['clientID']
    parameter=file_content['parameter']
    while not mqtt_flag:
        try:
            broker=requests.get(serviceCatalogAddress+'/broker').json()
            broker_IP=broker.get('IP_address')
            broker_port=broker.get('port')
            data_topic=broker['topic'].get('actuators')
            base_topic="{}{}/{}".format(data_topic,platform_ID,room_ID)
            myLED=LED(clientID,base_topic,broker_IP,broker_port,parameter,pin)
            myLED.setup()
            time.sleep(1)
            myLED.run()
            mqtt_flag=True
        except Exception as e:
            print("Can't connect to mqtt broker. New attempt...")
            print(e)
            time.sleep(30)
            
    time.sleep(1)
    myLED.create_info()
    thread1=pingThread(1,platform_ID,room_ID,myLED._data,serviceCatalogAddress)
    thread1.start()
    time.sleep(1)
    if thread1.connection_flag:
        thread2=ReceiveCommandThread(2,myLED)
        thread2.start()

