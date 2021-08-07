from RPLCD import CharLCD
import RPi.GPIO as GPIO
import requests
import time

class LCD(object):
    def __init__(self):
        
        self.lcd= CharLCD(numbering_mode=GPIO.BOARD, cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33,31,29,23])
    
    def retrieveData(self,parameter):
        self.parameter=parameter
        self.value=int(float(requests.get('http://127.0.0.1:8081'+'/'+parameter).json()))
        #print(self.value)
        return self.value

    def Display(self,temperature,humidity,AQI):
        if temperature is not None and humidity is not None:
            self.lcd.cursor_pos= (0,0)
            self.lcd.write_string("Temp Hum  AQI")
            self.lcd.cursor_pos= (1,0)
            self.lcd.write_string(str(temperature)+' C '+str(humidity)+'% '+str(AQI)+' ppm')
            
if __name__ == '__main__':
    lcd=LCD()
    while True:
        temperature=lcd.retrieveData('temperature')
        humidity=lcd.retrieveData('humidity')  
        AQI=lcd.retrieveData('AQI')
        lcd.Display(temperature,humidity,AQI)
        #time.sleep(1)
        
    

