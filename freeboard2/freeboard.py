import cherrypy
import json
import os

class Freeboard_deployer(object):
	exposed=True

	def GET(self,*uri,**params):
		if (len(uri) > 0 and uri[0] == "day"):
			return open("index_day.html")
		elif (len(uri) > 0 and uri[0] == "week"):
			return open("index_week.html")
		elif (len(uri) > 0 and uri[0] == "month"):
			return open("index_month.html")
		elif (len(uri) > 0 and uri[0] == "actual"):
			return open("index_actual.html")
		else:
			#raise cherrypy.HTTPError(404, "Error uri[0] must be  'day'")
			return open("index.html")
	
	def POST (self, *uri, **params):
		body = str(params['json_string'])
		f= open("./dashboard/dashboard_actual.json",'w+')
		f.write(body)
		f.close()
		return 

if __name__ == '__main__':
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.staticdir.root': os.path.abspath(os.getcwd()),
			'tools.sessions.on': True
		},
		##LINES ADDED TO PROVIDE THE PATH FOR CSS
		'/css':{
			'tools.staticdir.on': True, 
			'tools.staticdir.dir':'./css' 
		},
		##LINES ADDED TO PROVIDE THE PATH FOR JS
		'/js':{
			'tools.staticdir.on': True, 
			'tools.staticdir.dir':'./js' 
		},
		'/img':{
			'tools.staticdir.on': True, 
			'tools.staticdir.dir':'./img' 
		},
		'/dashboard':{
			'tools.staticdir.on': True, 
			'tools.staticdir.dir':'./dashboard' 
		},
		'/plugins/freeboard':{
			'tools.staticdir.on': True, 
			'tools.staticdir.dir':'./plugins/freeboard' 
		},
		'/plugins/mqtt':{
			'tools.staticdir.on': True, 
			'tools.staticdir.dir':'./plugins/mqtt' 
		},
		'/plugins/thirdparty':{
			'tools.staticdir.on': True, 
			'tools.staticdir.dir':'./plugins/thirdparty' 
		}
	}
	cherrypy.tree.mount(Freeboard_deployer(), '/', conf)
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.config.update({'server.socket_port': 8080})
	cherrypy.engine.start()
	cherrypy.engine.block()
