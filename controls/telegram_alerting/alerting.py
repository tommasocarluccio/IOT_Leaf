import time
import sys
from etc.warning_class import *

class AlertingControl(warningControl):
    def __init__(self,conf_filename):
        warning_class.__init__(self,conf_filename)

    def notify(self,topic,msg):
        payload=json.loads(msg)
        platform_ID=payload['bn'].split("/")[0]
        room_ID=payload['bn'].split("/")[1]
        device_ID=payload['bn'].split("/")[2]
        e=payload['e']
        profiles_catalog=requests.get(self.serviceCatalogAddress+'/profiles_catalog').json()['url']
        response=requests.get("{}/{}/rooms/{}/preferences/thresholds".format(profiles_catalog,platform_ID,room_ID))
        if response.status_code==200:
            th_dict=response.json()
            for meas in e:
                parameter=meas['n']
                try:
                    warning_cmd=self.compare_value(th_dict[parameter]["min"],th_dict[parameter]["max"],meas['v'])
                    topic=self.retrieve_topic(platform_ID,room_ID,parameter+"_warning") 
                    if topic is not False:
                        self.pub.publish(topic,json.dumps(warning_cmd))
                    if warning_cmd:
                        print("Warning sent to {}-{}".format(platform_ID,room_ID))      
                except Exception as e:
                    print(e)


if __name__ == '__main__':
    conf=sys.argv[1]
    clientID="alerting_control"
    c=AlertingControl(conf)
    while not c.setup(clientID):
        print("Try again..")
        time.sleep(10)
    while True:
        time.sleep(1)