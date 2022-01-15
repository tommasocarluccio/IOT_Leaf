
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from etc.MyMQTT import *
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import sys
import json
import requests
import threading

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
        
class OLED():
    def __init__(self,clientID,base_topic,broker_IP,broker_port):
        self.broker_IP=broker_IP
        self.broker_port=broker_port
        self.temp=None
        self.hum=None
        self.aqi=None
        self.AQI="NONE"
        self.clientID=clientID
        self.topic=base_topic+"/"+self.clientID
    def create_info(self):
        e=[]
        resource={"n":None,"u":None,"topic":self.topic}
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
        try:
            payload=json.loads(msg)
            #print(payload)
            for element in payload["e"]:
                parameter=element['n']
                value=element['v']
                unit=element['u']
                timestamp=element['t']
                    
                print(f'{parameter}:{value} {unit} - {timestamp}')
                if(parameter=="temperature"):
                    self.temp=round(value,2)
                    #self.draw.text((self.x+6, self.top+8),     str("Temp.")+ "   " + str(value)+"°"+unit, font=self.font, fill=255)

                if(parameter=="humidity"):
                    self.hum=round(value,2)
                    #self.draw.text((self.x+6, self.top+16),    str("Hum.")+ "    " + str(value)+unit,  font=self.font, fill=255)
                if(parameter=="AQI"):
                    self.aqi=round(value,2)
                    if(value <=300):
                        self.AQI="GOOD"
                    elif(value>300 and value <=650):
                        self.AQI="BAD"
                    elif(value>650):
                        self.AQI="UNSAFE"
                    else:
                        self.AQI="NONE"
            self.draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)
            self.draw.text((self.x+55, self.top),     "LEAF", font=self.font, fill=255)
            self.draw.text((self.x+6, self.top+16),     str("Temp.")+ "   " + str(self.temp)+"°C", font=self.font, fill=255)
            self.draw.text((self.x+6, self.top+8),       "AQI:    " +str(self.aqi),  font=self.font, fill=255)
            self.draw.text((self.x+66, self.top+8),       "    " +str(self.AQI),  font=self.font, fill=255)
            
            self.draw.text((self.x+6, self.top+24),    str("Hum.")+ "    " + str(self.hum)+"%",  font=self.font, fill=255)
            # Display image.
            self.disp.image(self.image)
            self.disp.display()
            time.sleep(.1)
        except Exception as e:
            print(e)
            pass
            

    def initializeDisplay(self):
        RST = None   
        DC = 23
        SPI_PORT = 0
        SPI_DEVICE = 0

        
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
        self.disp.begin()
        self.disp.clear()
        self.disp.display()

        width = self.disp.width
        height = self.disp.height
        self.image = Image.new('1', (width, height))

        self.draw = ImageDraw.Draw(self.image)

        self.draw.rectangle((0,0,width,height), outline=0, fill=0)

        padding = -2
        self.top = padding
        self.bottom = height-padding

        self.x = 0
        # Load default font.
        self.font = ImageFont.load_default()
        #self.font = ImageFont.truetype('font/coolvetica rg.otf', 10)
        self.draw.rectangle((0,0,width,height), outline=0, fill=0)
        self.draw.text((self.x+6, self.top+8), "Connecting...", font=self.font, fill=255)
        self.disp.image(self.image)
        self.disp.display()
        time.sleep(.1)
        
        
if __name__=='__main__':
    filename=sys.argv[1]
    platform_ID=sys.argv[2]
    room_ID=sys.argv[3]
    mqtt_flag=False
    file_content=json.load(open(filename,"r"))
    serviceCatalogAddress=file_content['service_catalog']
    
    clientID=file_content['clientID']
        
    while not mqtt_flag:
        try:
            broker=requests.get(serviceCatalogAddress+'/broker').json()
            broker_IP=broker.get('IP_address')
            broker_port=broker.get('port')
            data_topic=broker['topic'].get('data')
            base_topic="{}{}/{}".format(data_topic,platform_ID,room_ID)
            myOLED=OLED(clientID,base_topic,broker_IP,broker_port)
            myOLED.initializeDisplay()
            myOLED.setup()
            time.sleep(1)
            myOLED.run()
            mqtt_flag=True
        except Exception as e:
            #print(e)
            print("Can't connect to mqtt broker. New attempt...")
            time.sleep(30)
            
    time.sleep(1)
    #myOLED.create_info()
    thread1=pingThread(1,platform_ID,room_ID,myOLED._data,serviceCatalogAddress)
    thread1.start()

    myOLED.follow(data_topic+platform_ID+"/"+room_ID+"/#")
    while True:
        time.sleep(3)
    myOLED.draw.rectangle((0,0,myOLED.disp.width,myOLED.disp.height), outline=0, fill=0)
    myOLED.disp.display()
    myOLED.stop()

