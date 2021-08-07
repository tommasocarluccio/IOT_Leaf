from Generic_Sensor import *
import time
import Adafruit_DHT
import json
from datetime import datetime

class DHT11(SensorPublisher):
    def __init__(self,configuration_filename):
        SensorPublisher.__init__(self,configuration_filename)
        self.DHT11 = Adafruit_DHT.DHT11                                  
        self.DHT11_PIN = 4
        print(self.sensorID)
        
               
    def sendData(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.DHT11, self.DHT11_PIN, retries=2, delay_seconds=5)
        outputResult=[{'parameter':'humidity','value':humidity},{'parameter':'temperature','value':temperature}]
        self.PublishData(outputResult)
            
if __name__ == '__main__':
   
    sensor=DHT11('dht11_settings.json')
    sensor.start()
    while True:

        sensor.sendData()
        sensor.pingCatalog()
        time.sleep(5)

