from etc.Generic_Sensor import *
import time
import adafruit_dht

class dht11(SensorPublisher):
    def __init__(self,configuration_filename,broker_ip,broker_port,data_topic,platform_ID,room_ID,device_ID='dht11',pin=17):
        SensorPublisher.__init__(self,configuration_filename,platform_ID,room_ID,device_ID,broker_ip,broker_port,data_topic)
        self.DHT11 = adafruit_dht.DHT11(pin)                                  
                    
    def retrieveData(self):
        try:
            outputResult=[]
            humidity=self.DHT11.humidity
            temperature = self.DHT11.temperature
            timestamp=time.time()
            if humidity is not None:
                outputResult.append({'parameter':'humidity','value':humidity,'time':timestamp})  
            if temperature is not None:
                outputResult.append({'parameter':'temperature','value':temperature,'time':timestamp})  
            
            return outputResult
        except Exception as e:
            #print(e)
            pass
            
