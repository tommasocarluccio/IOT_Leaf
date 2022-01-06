import time
import sys
from etc.warning_class import *

class AlertingControl(warningControl):
    def __init__(self,conf_filename):
        warningControl.__init__(self,conf_filename)
        self.bot_url=requests.get(self.serviceCatalogAddress+'/telegram_bot').json()['url']
        self.adaptor_url=requests.get(self.serviceCatalogAddress+'/database_adaptor').json()['url']
        self.logs={}

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
                    #avg_value=requests.get(self.adaptor_url+'/'+platform_ID+'/'+room_ID+'/check_warning?parameter='+parameter+"&time=60").json()
                    print(parameter+": measured value "+str(meas['v']))
                    status=self.compare_value(th_dict[parameter]["min"],th_dict[parameter]["max"],meas['v'])
                    if status is not False:
                        
                        avg_value=requests.get(self.adaptor_url+'/'+platform_ID+'/'+room_ID+'/check_warning?parameter='+parameter+"&time=60").json()
                        avg_status=self.compare_value(th_dict[parameter]["min"],th_dict[parameter]["max"],avg_value)
                        """
                        room_data=requests.get(self.adaptor_url+'/'+platform_ID+'/'+room_ID+'/now').json()
                        for key,value in room_data.items():

                            if value[0]==parameter:
                                #print(value[1])
                                print(parameter+": last value "+str(value[1]))
                                last_value=self.compare_value(th_dict[parameter]["min"],th_dict[parameter]["max"],int(value[1]))
                                #print(last_value)
                        """
                        if avg_status is not False:
                            if not self.check_last_log(platform_ID,room_ID,parameter,status):
                                msg=self.create_msg(parameter,status)
                                self.logs[platform_ID][room_ID][parameter]={"status":status,"timestamp":time.time()}
                                print(self.logs)
                                try:
                                    requests.post(self.bot_url+'/warning/'+platform_ID+'/'+room_ID, json=msg)
                                    print("{}-{}. Sending Message:".format(platform_ID,room_ID))
                                    print(msg) 
                                except:
                                    print("Bot Communication failed")

                except Exception as e:
                    print(e)
    def create_msg(self,parameter, status):
        msg=self.conf_content['msg']
        msg['parameter']=parameter
        msg['status']=status
        msg['tip']=self.retrieve_tip(parameter,status)
        return msg

    def compare_value(self,minimum,maximum,value):
        if float(value)<float(minimum):
            return "LOW"   
        elif float(value)>=float(maximum):
            return "HIGH"
        else:
            return False

    def retrieve_tip(self,parameter,status):
        tips_catalog=requests.get(self.serviceCatalogAddress+'/tips_catalog').json()['url']
        tip=requests.get(tips_catalog+"/tip/"+parameter+"/"+status)
        if tip.status_code==200:
            return tip.text
        else:
            return None

    def check_last_log(self, platform_ID,room_ID,parameter,status):
        last_status=self.logs[platform_ID][room_ID][parameter].get('status')
        last_time=self.logs[platform_ID][room_ID][parameter].get('timestamp')
        if last_status is not status and time.time()-last_time<5:
            return True
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