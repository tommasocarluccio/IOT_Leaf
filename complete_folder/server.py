import cherrypy
import json
from adapter import Adapter 

class Server(object):
	exposed=True

	def __init__(self):
		self.s=Adapter()
	def GET(self,*uri):
		result=False
            
		if len(uri)!=0:
			command= str(uri[0])

			if command=='temperature':
			    result=self.s.showTemp()
			    print(result)
			elif command=='humidity':
			    result=self.s.showHum()
			elif command=='AQI':
			    result=self.s.showAqi()
			    print(result)
			else:
                            raise cherrypy.HTTPError(501, "No operation!")
			if result==False:
                            raise cherrypy.HTTPError(404,"Not found")
			else:
			    return result
		
	def PUT(self,*uri):
		body=cherrypy.request.body.read()
		json_body=json.loads(body.decode('utf-8'))
		print(json_body)
		if str(uri[0])=='temperature':
			result=self.s.addTemp(json_body['value'])
			return result
			#print(self.s.temperature)
		elif uri[0]=='humidity':
			result=self.s.addHum(json_body['value'])
			#print(self.s.humidity)
			return result
		elif uri[0]=='AQI':
			result=self.s.addAqi(json_body['value'])
			return result
		
	
if __name__ == '__main__':
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True
		}
	}
	cherrypy.tree.mount(Server(), '/', conf)
	cherrypy.config.update({'server.socket_host': '127.0.0.1'})
	cherrypy.config.update({'server.socket_port': 8081})
	cherrypy.engine.start()
	cherrypy.engine.block()
