from RPLCD import CharLCD
from conf.adapter import Adapter
import RPi.GPIO as GPIO
import time
import json

class LCDAdapter(Adapter):
    def __init__(self,room_filename):
        Adapter.__init__(self,room_filename)
        GPIO.setwarnings(False)
        self.message={'Temperature':'','Humidity':'','AQI':''}
        self.lcd= CharLCD(numbering_mode=GPIO.BOARD, cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33,31,29,23])
        
    def runLCD(self):
        print("LCD display is now running\n")
         
    def Display(self,temperature,humidity,AQI):
        if temperature == None:
            temperature=' /'
        if humidity == None:
            humidity='/ '
        if AQI == None:
            AQI='  /'
        self.lcd.cursor_pos= (0,0)
        self.lcd.write_string("Temp Hum  AQI")
        self.lcd.cursor_pos= (1,0)
        self.lcd.write_string(str(temperature)+' C '+str(humidity)+'% '+str(AQI)+' ppm')
        
    def warning(self,flag):
        GPIO.setup(40,GPIO.OUT)
        if flag==True:
            GPIO.output(40,GPIO.HIGH)
        else:
            GPIO.output(40,GPIO.LOW)
            
    def configurationLed(self,flag):
        self.DisplayReset()
        GPIO.setup(40,GPIO.OUT)
        self.connectionAttempt()
        
        if flag==True:
            GPIO.output(40,GPIO.LOW)
            self.lcd.cursor_pos= (1,0)
            self.lcd.write_string("Connection: OK")
        else:
            self.lcd.cursor_pos= (1,0)
            self.lcd.write_string("Connection: No")
            
    def errorPrinting(self):
        self.DisplayReset()
        GPIO.setup(40,GPIO.OUT)
        self.lcd.cursor_pos= (1,0)
        self.connectionAttempt()
        self.lcd.write_string("Procedure failed")
        GPIO.output(40,GPIO.LOW)
        
    def connectionAttempt(self):
        start_time=time.time()
        while time.time()-start_time < 4:
            self.lcd.cursor_pos= (0,0)
            self.lcd.write_string("     %Leaf%")
            self.lcd.cursor_pos= (1,0)
            self.lcd.write_string(" ..Connecting..")
            GPIO.output(40,GPIO.HIGH)
            time.sleep(0.6)
            GPIO.output(40,GPIO.LOW)
            time.sleep(0.4)
        self.DisplayReset()
        self.lcd.cursor_pos= (0,0)
        self.lcd.write_string("     %Leaf%")
        self.lcd.cursor_pos= (1,0)
                
    def DisplayReset(self):
        self.lcd.clear()
        time.sleep(0.7)
        
                  
if __name__ == '__main__':
    maxAttempts=3
    lcd=LCDAdapter('conf/etc/room_settings.json')
    lcd.runLCD()
    lcd.DisplayReset()
    errorFlag=0
    startTime=time.time()
    while True:
        try:
            lcd.findDevices()
            sensorTemperature=lcd.identifySensor('temperature')
            sensorHumidity=lcd.identifySensor('humidity')
            sensorAQI=lcd.identifySensor('AQI')
            temperature=lcd.retrieveData(sensorTemperature,'temperature')
            humidity=lcd.retrieveData(sensorHumidity,'humidity')  
            AQI=lcd.retrieveData(sensorAQI,'AQI')
            actualTime=time.time()
            if actualTime-startTime>20:
                messageTS=lcd.sendThingSpeak(temperature,humidity,AQI)
                print(messageTS)
                startTime=actualTime
            if AQI!=None and AQI >999:
                AQI=999
                lcd.warning(True)
            else:
                lcd.warning(False)
            lcd.Display(temperature,humidity,AQI)
            errorFlag=0
        except:
            lcd.errorPrinting()
            errorFlag=errorFlag+1
            if errorFlag==maxAttempts:
                print(str(maxAttempts) + " attempts performed: no Catalogue is now available.\nExiting...\n")
                break
            time.sleep(15)
        #time.sleep(1)