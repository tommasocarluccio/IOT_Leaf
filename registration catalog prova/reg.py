import cherrypy
import json
import sys
import os
import requests

class Registration_deployer(object):
    exposed=True
    def __init__(self,filename):
        self.filename=filename
        self.registration_configuration=json.load(open(self.filename,"r"))
        self.serviceCatalogAddress=self.registration_configuration['service_catalog']
        self.registrationServiceName=self.registration_configuration['service_name']
        self.registrationServiceIP=self.registration_configuration['IP_address']
        self.registrationServicePort=self.registration_configuration['IP_port']

    def registerRequest(self):
        msg={"service":self.registrationServiceName,"IP_address":self.registrationServiceIP,"port":self.registrationServicePort}
        try:
            service=requests.post(f'{self.serviceCatalogAddress}/register',json=msg).json()
            return service
        except IndexError as e:
            #print(e)
            print("Failure in registration.")
            return False

        
    def GET(self,*uri,**params):
        if (len(uri))>0 and uri[0]=="reg.html":
            return open('reg.html')

        elif (len(uri)>0 and uri[0]=="reg_results"):
            users=json.load(open('reg.json'))
            for user in users.get("users"):
                if user['user_ID']==params['userID']:
                    return open("fail_reg_user.html") 
            if params['psw']!=params['psw-repeat']:
                return open("fail_reg_pass.html") 

            else:
                users["users"].append({
                    "user_ID":params['userID'],
                    "catalog_id":params['catalogID'],
                    "password":params['psw']
                    })
                with open('reg.json', 'w') as outfile:
                    json.dump(users, outfile, indent=4)
            
                return open("correct_reg.html")

if __name__ == '__main__':
    filename=sys.argv[1]
    registrationService=Registration_deployer(filename)
    if registrationService.registerRequest() is not False:
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.sessions.on': True
            }
        }
        
        cherrypy.tree.mount(registrationService, registrationService.registrationServiceName, conf)
        cherrypy.config.update({'server.socket_host': registrationService.registrationServiceIP})
        cherrypy.config.update({'server.socket_port': registrationService.registrationServicePort}) 
        cherrypy.engine.start()
        cherrypy.engine.block()
    else:
        print("Exiting...")

