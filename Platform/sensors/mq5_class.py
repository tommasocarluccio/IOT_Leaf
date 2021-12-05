from etc.Generic_Sensor import*
import time
import serial
import sys

class mq5(SensorPublisher):
    def __init__(self,configuration_filename='mq5_settings.json',device_ID="mq5",serialPort='/dev/ttyACM0'):
        SensorPublisher.__init__(self,configuration_filename,device_ID)
        self.ser = serial.Serial(serialPort, 9600, timeout=0.5)
       
    def retrieveData(self):
        outputResult=[]
        timestamp=time.time()
        try:
            self.ser.flush()
            gas=int(self.ser.readline().decode('utf-8').rstrip())
            #print(gas) 
        except:
            gas=None     
        outputResult.append({'parameter':'AQI','value':gas,'time':timestamp})
        if gas is not None:
            return outputResult
           