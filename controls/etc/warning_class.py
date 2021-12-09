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
				#if parameter=='AQI':
				print(parameter)
				try:
					warning_cmd=self.compare_value(th_dict[parameter]["min"],th_dict[parameter]["max"],meas['v'])
					pub=sendWarning(self.clientID+"_pub",self.broker_IP,self.broker_port,self)
					pub.run()
					pub.publish("{}{}/{}/LED".format(self.data_topic,platform_ID,room_ID),json.dumps(warning_cmd))		
					pub.end()
				except Exception as e:
					print(e)


	def compare_value(self,minimum,maximum,value):
		if value<minimum or value>maximum:
			return True
			
		else:
			return False


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








