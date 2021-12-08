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
		    data:topic=broker['topic'].get('data')
		    self.subscriber=DataCollector(clientID,broker_IP,broker_port,self)
		    self.subscriber.run()
		    """
		    for platform in requests.get(resource_catalog['url']+"/platformsList").json():
		        self.adaptor.subscriber.follow(platform+'/#')
		    """
		    self.subscriber.follow('data/#')
		    return True
		except Exception as e:
		    print(e)
		    print("MQTT Subscriber not created")
		    return False

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
						self.last_p=parameter['n']
			return params
		except Exception as e:
			print(e)
			return False

	def send(self,command,params):
		try:
			#print(params)
			r=requests.post("{}{}".format(self.thingspeak_url,command),params=params)
			if r.status_code==200:
				self.last_msg_time=time.time()
				return True
			else:
				return False
		except Exception as e:
			print(e)
			return False

	def notify(self,topic,msg):
		try:
			payload=json.loads(msg)
			#print(payload)
			platform_ID=payload['bn'].split("/")[0]
			room_ID=payload['bn'].split("/")[1]
			device_ID=payload['bn'].split("/")[2]
			e=payload['e']

			if time.time()-self.last_msg_time>self.delta:
				params=self.retrieve_info(e,platform_ID)
				if params is not False:
					print("Sending data for {}-{}".format(platform_ID,room_ID))
					if self.send("update",params):
						print(e)
						print("Success!\n")
					else:
						print("Failed!\n")
				else:
					print("Failed!\n")

				
		except Exception as e:
			print(e)
   








