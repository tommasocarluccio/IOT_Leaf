from etc.Generic_Sensor import *
import time
import adafruit_dht

class dht11(SensorPublisher):
    def __init__(self,configuration_filename,device_ID='dht11',pin=17):
        SensorPublisher.__init__(self,configuration_filename,device_ID)
        self.DHT11 = adafruit_dht.DHT11(pin)                                  
                    
    def retrieveData(self):
        try:
            humidity=self.DHT11.humidity
            temperature = self.DHT11.temperature
            timestamp=time.time()
            outputResult=[{'parameter':'humidity','value':humidity,'time':timestamp},{'parameter':'temperature','value':temperature,'time':timestamp}]
            return outputResult
        except:
            pass
            
