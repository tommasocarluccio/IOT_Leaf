from etc.Generic_Sensor import*
import time
import serial
import sys

class mq135(SensorPublisher):
    def __init__(self,configuration_filename,broker_ip,broker_port,data_topic,platform_ID,room_ID,device_ID='mq135',serialPort='/dev/ttyACM0'):
        SensorPublisher.__init__(self,configuration_filename,platform_ID,room_ID,device_ID,broker_ip,broker_port,data_topic)
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
        if gas is not None and gas<1000:
            return outputResult
           