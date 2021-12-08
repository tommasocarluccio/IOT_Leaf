
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

import subprocess

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

class OLED():
    def __init__(self,clientID,broker_IP,broker_port):
        self.broker_IP=broker_IP
        self.broker_port=broker_port
        self.temp=0
        self.hum=0
        self.aqi=0
        self.AQI="NONE"
        self.clientID=clientID
        
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
                if(value <=600):
                    self.AQI="GOOD"
                elif(value>600 and value <=750):
                    self.AQI="BAD"
                elif(value>750):
                    self.AQI="UNSAFE"
                else:
                    self.AQI="NONE"
            self.draw.rectangle((0,0,self.disp.width,self.disp.height), outline=0, fill=0)
            self.draw.text((self.x+55, self.top),     "LEAF", font=self.font, fill=255)
            self.draw.text((self.x+6, self.top+16),     str("Temp.")+ "   " + str(self.temp)+"°C", font=self.font, fill=255)
            #self.draw.text((self.x+6, self.top+25),    str("Wind")+ "    " + str(self.wind)+" "+"kmH",  font=self.font, fill=255)        
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
        RST = None     # on the PiOLED this pin isnt used
        # Note the following are only used with SPI:
        DC = 23
        SPI_PORT = 0
        SPI_DEVICE = 0

        
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

        # Initialize library.
        self.disp.begin()

        # Clear display.
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
    mqtt_flag=False
    
    roomContent=json.load(open("../room/conf/room_settings.json","r"))
    room_ID=roomContent['room_info']['room_ID']
    platform_ID=roomContent['platform_ID']
    serviceCatalogAddress=roomContent['service_catalog']
        
    while not mqtt_flag:
        try:
            broker=requests.get(serviceCatalogAddress+'/broker').json()
            broker_IP=broker.get('IP_address')
            broker_port=broker.get('port')
            myOLED=OLED("DISPLAY",broker_IP,broker_port)
            myOLED.initializeDisplay()
            myOLED.run()
            mqtt_flag=True
        except:
            print("Can't connect to mqtt broker. New attempt...")
            time.sleep(30)
            
    time.sleep(1)
    myOLED.follow(platform_ID+"/"+room_ID+"/#")
    while True:
        time.sleep(3)
    myOLED.draw.rectangle((0,0,myOLED.disp.width,myOLED.disp.height), outline=0, fill=0)
    myOLED.disp.display()
    myOLED.stop()

