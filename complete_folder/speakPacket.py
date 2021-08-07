import cherrypy
import json
import requests
import time

class FinalData(object):
	def __init__(self):
		self.message={'Temperature':'','Humidity':'','AQI':''}
	def sendData(self):
		try:
			r1=requests.get('http://0.0.0.0:8080/temp')
			temp=r1.json()
			r2=requests.get('http://0.0.0.0:8080/hum')
			hum=r2.json()
			r3=requests.get('http://0.0.0.0:8080/aqi')
			aqi=r3.json()
		except:
			temp=None
			hum=None
			aqi=None

		self.message['Humidity']=str(hum)	
		self.message['Temperature']=str(temp)
		self.message['AQI']=str(aqi)

		if (temp is not None and hum is not None and aqi is not None):
			params={'field3':self.message['Temperature'],'field5': self.message['Humidity'],'field1':self.message['AQI']}
			url='https://api.thingspeak.com/update?api_key=1G5BT51PIND6DGZY'
			r=requests.post(url,params=params)
			return self.message

if __name__ == '__main__':
	data=FinalData()
	while True:
		r=data.sendData()
		print(r)
		time.sleep(15)



