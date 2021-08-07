from Generic_Sensor import *
import time
import Adafruit_DHT
import sys

class DHT11(SensorPublisher):
    def __init__(self,configuration_filename='dht11_settings.json',room_filename='room_settings.json',pin=4):
        SensorPublisher.__init__(self,configuration_filename,room_filename)
        self.DHT11 = Adafruit_DHT.DHT11                                  
        self.DHT11_PIN = pin
                    
    def sendData(self):
        humidity, temperature = Adafruit_DHT.read_retry(self.DHT11, self.DHT11_PIN, retries=2, delay_seconds=3)
        outputResult=[{'parameter':'humidity','value':humidity},{'parameter':'temperature','value':temperature}]
        self.PublishData(outputResult)
            
if __name__ == '__main__':
    settingFile=sys.argv[1]
    roomFile=sys.argv[2]
    pin=sys.argv[3]
    sensor=DHT11(settingFile,roomFile,pin)
    sensor.start()
    #sensor.updateRoom()
    while True:
        sensor.sendData()
        sensor.pingCatalog()
        time.sleep(5)

