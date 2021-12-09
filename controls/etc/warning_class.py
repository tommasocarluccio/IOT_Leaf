import json
import time
from datetime import datetime
from etc.MyMQTT import *
import requests

class warningControl():
	def __init__(self,conf_filename):
		self.conf_content=json.load(open(conf_filename,"r"))
		self.serviceCatalogAddress=self.conf_content['service_catalog']
	def setup(self,clientID):
		try:
		    broker=requests.get(self.serviceCatalogAddress+'/broker').json()
		    broker_IP=broker.get('IP_address')
		    broker_port=broker.get('port')
		    data_topic=broker['topic'].get('data')
		    self.subscriber=DataCollector(clientID,broker_IP,broker_port,self)
		    self.subscriber.run()
		    self.subscriber.follow(data_topic+'#')
		    return True
		except Exception as e:
		    print(e)
		    print("MQTT Subscriber not created")
		    return False
    def notify(self,topic,msg):
		payload=json.loads(msg)
		platform_ID=payload['bn'].split("/")[0]
		room_ID=payload['bn'].split("/")[1]
		device_ID=payload['bn'].split("/")[2]
		e=payload['e']
		self.check_threshold(platform_ID,room_ID,e)
	def check_threshold(self,platform_ID,room_ID,e):
		profiles_catalog=requests.get(self.serviceCatalogAddress+'/profiles_catalog').json()['url']
		for meas in e:
			parameter=meas['n']
			

class DataCollector():
	def __init__(self,clientID,brokerIP,brokerPort,notifier):
	    self.clientID=clientID
	    self.brokerIP=brokerIP
	    self.brokerPort=brokerPort
	    self.notifier=notifier
	    self.client=MyMQTT(self.clientID,self.brokerIP,self.brokerPort,self)
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



class sendWarning():
	def __init__(self,clientID,brokerIP,brokerPort,notifier):
		self.clientID=clientID
		self.brokerIP=brokerIP
		self.brokerPort=brokerPort
		self.notifier=notifier
		self.client=MyMQTT(self.clientID,self.brokerIP,self.brokerPort,self.notifier)
	def run(self):
		self.client.start()
		print('{} has started'.format(self.clientID))
	def publish(self,topic,msg):
		self.client.myPublish(topic,msg)
	def end(self):
		self.client.stop()
		print('{} has stopped'.format(self.clientID))








