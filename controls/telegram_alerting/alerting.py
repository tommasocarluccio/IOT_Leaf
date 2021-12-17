import time
import sys
from etc.warning_class import *

class AlertingControl(warningControl):
    def __init__(self,conf_filename):
        warningControl.__init__(self,conf_filename)
        self.bot_url=requests.get(self.serviceCatalogAddress+'/telegram_bot').json()['url']

    def setup(self,clientID):
        try:
            broker=requests.get(self.serviceCatalogAddress+'/broker').json()
            self.broker_IP=broker.get('IP_address')
            self.broker_port=broker.get('port')
            self.data_topic=broker['topic'].get('data')
            self.clientID=clientID
            self.subscriber=DataCollector(self.clientID,self.broker_IP,self.broker_port,self)
            self.subscriber.run()
            self.subscriber.follow(self.data_topic+'#')
            return True
        except Exception as e:
            print(e)
            print("MQTT Subscriber not created")
            self.subscriber.end()
            return False

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
                    status=self.compare_value(th_dict[parameter]["min"],th_dict[parameter]["max"],meas['v'])
                    if status is not False:
                        msg=self.create_msg(parameter,status)

                        r=requests.post(self.bot_url+'/warning/'+platform_ID+'/'+room_ID, json=msg)
                        if r.status_code==200:
                            print("{}-{}. Sending Message:".format(platform_ID,room_ID))
                            print(msg) 
                        else:
                            print("Bot Communication failed!")
                except Exception as e:
                    print(e)
    def create_msg(self,parameter, status):
        msg=self.conf_content['msg']
        msg['parameter']=parameter
        msg['status']=status
        return msg

    def compare_value(self,minimum,maximum,value):
        if float(value)<float(minimum):
            return "LOW"   
        elif float(value)>=float(maximum):
            return "HIGH"
        else:
            return False


if __name__ == '__main__':
    conf=sys.argv[1]
    clientID="alerting_control"
    c=AlertingControl(conf)
    while not c.setup(clientID):
        print("Try again..")
        time.sleep(10)
    while True:
        time.sleep(1)