from Generic_Sensor import*
import time
import json
from datetime import datetime
import serial

class Mq5(SensorPublisher):
    def __init__(self,configuration_filename):
        SensorPublisher.__init__(self,configuration_filename)
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0.5)
        print(self.sensorID)
       
    def sendData(self):
        try:
            self.ser.flush()
            gas=int(self.ser.readline().decode('utf-8').rstrip())
            #print(gas) 
        except:
            gas=None
            
        outputResult=[{'parameter':'AQI','value':gas}]
        self.PublishData(outputResult)
           
        

if __name__ == '__main__':
   
    sensor=Mq5('mq5_settings.json')
    sensor.start()
    while True:

        sensor.sendData()
        sensor.pingCatalog()
        time.sleep(0.5)
