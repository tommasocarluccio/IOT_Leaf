import json

class Adapter(object):
	def __init__(self):
		self.temperature=0
		self.humidity=0
		self.aqi=0
		self.welcomeString='WELCOME to LEAF- take control of your air, take control of your life!'
	def addTemp(self,value):
		self.temperature=value
		return self.temperature
	def addHum(self,value):
		self.humidity=value
		return self.humidity
	def addAqi(self,value):
		self.aqi=value
		return self.aqi
	def showTemp(self):
		return json.dumps(self.temperature,indent=4)
	def showHum(self):
		return json.dumps(self.humidity,indent=4)
	def showAqi(self):
		return json.dumps(self.aqi,indent=4)
	def showWelcome(self):
                return self.welcomeString


