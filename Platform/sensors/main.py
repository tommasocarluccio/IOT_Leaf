
import time
import sys

if __name__ == '__main__':
    settingFile=sys.argv[1]
    device_ID=sys.argv[2]
    pin=sys.argv[3]
    class_imported=__import__(device_ID+'_class')
    sensor_class=getattr(class_imported,device_ID)
    sensor=sensor_class(settingFile,device_ID,pin)

    if not sensor.load():
        print("Server connection failed.")
    else:
        print("Server connection performed.")
        last_time=time.time()
    time.sleep(1)
    sensor.start()
    while True:
        output=sensor.retrieveData()
        try:
            sensor.publishData(output)
            time.sleep(sensor.time_sleep)
        except:
            time.sleep(1)
    sensor.stop()
    
