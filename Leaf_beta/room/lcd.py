from RPLCD import CharLCD
import RPi.GPIO as GPIO
import requests
import time
import json
import sys

class LCDAdapter(object):
    def __init__(self,room_filename):
        configuration=json.load(open(room_filename))
        self.catalogURL=configuration['catalog']
        self.roomID=configuration['roomID']
        self.roomName=configuration['roomName']
        self.standardParameters=configuration['standard_parameters']
        self.thingSpeakURL=configuration['thingSpeakURL']
        
        self.message={'Temperature':'','Humidity':'','AQI':''}
        GPIO.setwarnings(False)
        self.lcd= CharLCD(numbering_mode=GPIO.BOARD, cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33,31,29,23])
        print("\n%% LEAF %%\n")
        
    def runLCD(self):
        print("LCD display is now running\n")
        print("Connected to "+self.thingSpeakURL)
        print("Standard resources are: "+ " ".join(x for x in self.standardParameters)+"\n")
        
    def findDevices(self):
        stringURL=self.catalogURL+'/rooms/'+self.roomID+'/devices'
        self.devices=requests.get(stringURL).json()
    
    def identifySensor(self,parameter):
        for dev in self.devices:
            for par in dev['parameters']:
                if par['parameter']==parameter:
                    output="{}\n{} is used for {}".format(self.roomID,dev['sensorID'],parameter)
                    #print(output)
                    return dev['sensorID']

    def retrieveData(self,sensorID,parameter):
        self.parameter=parameter
        try:
            stringURL=self.catalogURL+'/rooms/'+self.roomID+'/devices/'+sensorID+'?parameter='+parameter
            result=requests.get(stringURL).json()
            self.value=int(float(result['value']))
            return self.value
        except:
            return None

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
        
    def sendThingSpeak(self,temperature,humidity,AQI):
        self.message['Temperature']=temperature
        self.message['Humidity']=humidity   
        self.message['AQI']=AQI

        params={'field2':self.message['Temperature'],'field3': self.message['Humidity'],'field1':self.message['AQI']}
        url=self.thingSpeakURL
        try:
            r=requests.post(url,params=params)
            return self.message
        except:
            return "ThingSpeak unreachable"
                
    def DisplayReset(self):
        self.lcd.clear()
        time.sleep(0.7)
        
                  
if __name__ == '__main__':
    maxAttempts=3
    lcd=LCDAdapter('room_settings.json')
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
            lcd.Display(temperature,humidity,AQI)
            if AQI!=None and AQI >300:
                lcd.warning(True)
            else:
                lcd.warning(False)
            actualTime=time.time()
            if actualTime-startTime>20:
                messageTS=lcd.sendThingSpeak(temperature,humidity,AQI)
                print(messageTS)
                startTime=actualTime
            errorFlag=0
        except:
            lcd.errorPrinting()
            errorFlag=errorFlag+1
            if errorFlag==maxAttempts:
                print(str(maxAttempts) + " attempts performed: no Catalogue is now available.\nExiting...\n")
                break
            time.sleep(15)
        #time.sleep(1)