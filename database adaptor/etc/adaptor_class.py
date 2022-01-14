import json
import time
from datetime import datetime
from etc.generic_service import *
from etc.MyMQTT import *

class DataCollector():
    def __init__(self,clientID,brokerIP,brokerPort,notifier):
        self.clientID=clientID
        self.brokerIP=brokerIP
        self.brokerPort=brokerPort
        self.notifier=notifier
        self.client=MyMQTT(self.clientID,self.brokerIP,self.brokerPort,self.notifier)
    def run(self):
        self.client.start()
        print('{} has started'.format(self.clientID))
    def end(self):
        self.client.stop()
        print('{} has stopped'.format(self.clientID))
    def follow(self,topic):
        self.client.mySubscribe(topic)
    def unfollow(self,topic):
        self.client.unsubscribe(topic)


class Adaptor(Generic_Service):
    def __init__(self,conf_filename):
        Generic_Service.__init__(self,conf_filename)
        self.platforms_last=[]
        self.last_msg_time=time.time()
        self.delta=self.conf_content['delta']
        self.thingspeak_url=self.conf_content['thingspeak_url']
        
    def setup(self,clientID):
        try:
            broker=requests.get(self.serviceCatalogAddress+'/broker').json()
            #resource_catalog=requests.get(self.adaptor.serviceCatalogAddress+'/resource_catalog').json()
            broker_IP=broker.get('IP_address')
            broker_port=broker.get('port')
            data_topic=broker['topic'].get('data')
            self.subscriber=DataCollector(clientID,broker_IP,broker_port,self)
            self.subscriber.run()
            """
            for platform in requests.get(resource_catalog['url']+"/platformsList").json():
                self.adaptor.subscriber.follow(platform+'/#')
            """
            self.subscriber.follow(data_topic+'#')
            return True
        except Exception as e:
            print(e)
            print("MQTT Subscriber not created")
            return False
            
    #send individually measurments
    def retrieve_info(self,e,platform):
        try:
            clients_catalog=self.retrieveService('clients_catalog')
            clients_result=requests.get(clients_catalog['url']+"/info/"+platform+"/thingspeak").json()
            room_ID=clients_result['room']
            params={"api_key":clients_result["write_key"]}
            for parameter in e:
                for field in clients_result['fields']:
                    if clients_result['fields'].get(field)==parameter['n']:
                        params[field]=parameter["v"]
            return params
        except Exception as e:
            print(e)
            return False

    # 'pack' measurements to bypass thingspeak limitations
    def retrieve_info2(self,platform_ID,room_ID):
        for platform in self.platforms_last:
            if platform['platform_ID']==platform_ID:
                break
        try:
            clients_catalog=self.retrieveService('clients_catalog')
            clients_result=requests.get(clients_catalog['url']+"/info/"+platform_ID+"/thingspeak").json()
            for room in clients_result:
                if room['room']==room_ID:
                    break
            params={"api_key":room["write_key"]}
            for field in room['fields']:
                try:
                    params[field]=platform['measurements'][room['fields'].get(field)]
                except:
                    params[field]=None
            print(platform['measurements'])
            return params
        except Exception as e:
            print(e)
            return False

    def send(self,command,params):
        try:
            r=requests.post("{}{}".format(self.thingspeak_url,command),params=params)
            if r.status_code==200:
                self.last_msg_time=time.time()
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def create_platform_entry(self,platform_ID,e):
        if not any(plat['platform_ID']==platform_ID for plat in self.platforms_last):
            self.platforms_last.append({"platform_ID":platform_ID,"last_msg_time":time.time(),"measurements":{}})
        else:
            for platform in self.platforms_last:
                if platform["platform_ID"]==platform_ID:
                    for parameter in e:
                        n=parameter['n']
                        value=parameter['v']
                        platform['measurements'][n]=value

    def reset(self,platform_ID):
        index=self.find_pos(platform_ID)
        self.platforms_last[index]["last_msg_time"]=time.time()
        self.platforms_last[index]["measurements"]={}

    def find_pos(self,platform_ID):
        for index in range(len(self.platforms_last)):
                if self.platforms_last[index]["platform_ID"]==platform_ID:
                    return index

    def notify(self,topic,msg):
        try:
            payload=json.loads(msg)
            #print(payload)
            platform_ID=payload['bn'].split("/")[0]
            room_ID=payload['bn'].split("/")[1]
            device_ID=payload['bn'].split("/")[2]
            e=payload['e']

            self.create_platform_entry(platform_ID,e)
            if time.time()-self.platforms_last[self.find_pos(platform_ID)]['last_msg_time']>self.delta:
                params=self.retrieve_info2(platform_ID,room_ID)
                if params is not False:
                    print("Sending data for {}-{}".format(platform_ID,room_ID))
                    if self.send("update",params):
                        #print(e)
                        print("Success!\n")
                        self.reset(platform_ID)
                    else:
                        print("Failed!\n")
                else:
                    print("Failed!\n")
                
        except Exception as e:
            print(e)
