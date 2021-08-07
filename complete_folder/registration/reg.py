import cherrypy
import json
import os

class Registration_deployer(object):
	exposed=True
	def GET(self,*uri,**params):
		if (len(uri))>0 and uri[0]=="reg.html":
			return open('reg.html')

		elif (len(uri)>0 and uri[0]=="reg_results"):
			for user in users:
				if user['user_ID']==params['userID']:
					return open("fail_reg_user.html") 
			if params['psw']!=params['psw-repeat']:
				return open("fail_reg_pass.html") 

			else:
				users.append({
					"user_ID":params['userID'],
					"catalog_id":params['catalogID'],
					"password":params['psw']
					})
				with open('reg.json', 'w') as outfile:
					json.dump(users, outfile)
			
				return open("correct_reg.html")

if __name__ == '__main__':
	
	users=json.load(open('reg.json'))
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.staticdir.root': os.path.abspath(os.getcwd()),
			'tools.sessions.on': True
		}
	}
	cherrypy.tree.mount(Registration_deployer(), '/', conf)
	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.config.update({'server.socket_port': 9990})
	cherrypy.engine.start()
	cherrypy.engine.block()
