import cherrypy
import json
import os
import sys
import requests
import time
from clients_class import *

class Registration_deployer(object):
    exposed=True
    def __init__(self,filename):
        self.filename=filename
        self.catalog=ClientsCatalog(self.filename)
        self.serviceCatalogAddress=self.catalog.clientsContent['service_catalog']
        self.service_name=self.catalog.clientsContent['service_name']
        self.clientsCatalogIP=self.catalog.clientsContent['IP_address']
        self.clientsCatalogPort=self.catalog.clientsContent['IP_port']
        self.service=self.registerRequest()
        #self.flagNew=False

    def registerRequest(self):
        msg={"service":self.service_name,"IP_address":self.clientsCatalogIP,"port":self.clientsCatalogPort}
        try:
            service=requests.put(f'{self.serviceCatalogAddress}/register',json=msg).json()
            return service
        except Exception as e:
            print(e)
            print("Failure in  service registration.")
            return False

    def GET(self,*uri,**params):
        if (len(uri))>0 and uri[0]=="reg":
            return open('etc/reg.html')

        elif (len(uri)>0 and uri[0]=="reg_results"):
            check=self.catalog.check_registration(params['userID'],params['platformID'])
            if check is not False:
                html_error="etc/fail_reg_"+check+".html"
                return open(html_error)
                
            if params['psw']!=params['psw-repeat']:
                return open("etc/fail_reg_pass.html") 

            else:
                self.catalog.platforms.set_value(params['platformID'],"associated",True)
                self.catalog.users.content["users"].append({
                    "username":params['userID'],
                    "password":params['psw'],
                    "platforms_list":[params["platformID"]]
                    })
                self.catalog.users.save()
                self.catalog.platforms.save()
                #self.checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(self.catalog.userpassdict)
                #self.flagNew=True
                print("User '{}' correctly registered with platform '{}'\n".format(params['userID'],params['platformID']))
                return open("etc/correct_reg.html")
        elif(len(uri))>0 and uri[0]=="login":
        
            data=self.catalog.find_user(str(cherrypy.request.login)).copy()
            print(data)
            del data['password']
            return json.dumps(data)
        else:
            raise cherrypy.HTTPError(501, "No operation!")
            
    
    def DELETE(self,*uri):
        command=str(uri[0])
        if command=='removePlatform':
            username=uri[1]
            #username=str(cherrypy.request.login)
            platform_ID=uri[2]
            outputFlag=self.catalog.users.removePlatform(username,platform_ID)
            if outputFlag==True:
                output="Platform '{}' removed".format(platform_ID)
                self.catalog.platforms.set_value(platform_ID,"associated",False)
                self.catalog.users.save()
                self.catalog.platforms.save()
            else:
                #output="Platform '{}' not found ".format(platform_ID)
                raise cherrypy.HTTPError(404, "Platform not found")
        elif command=='removeUser':
            username=uri[1]
            outputFlag=self.catalog.users.removeUser(username)
            if outputFlag==True:
                output="User '{}' removed".format(username)
                self.catalog.users.save()
            else:
                raise cherrypy.HTTPError(404, "User not found")
        
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        print(output)
        result={"result":outputFlag}
        return json.dumps(result)
        
if __name__ == '__main__':
    clients_db=sys.argv[1]
    clientsCatalog=Registration_deployer(clients_db)
    get_ha1 = cherrypy.lib.auth_digest.get_ha1_dict_plain(clientsCatalog.catalog.users.userpassdict)
    clientsCatalog.checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(clientsCatalog.catalog.users.userpassdict)
    if clientsCatalog.service is not False:
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.sessions.on': True
            }
        }
        """
        conf = {
          'global' : {
            'server.socket_host' : clientsCatalog.clientsCatalogIP,
            'server.socket_port' : clientsCatalog.clientsCatalogPort,
            #'server.thread_pool' : 8
          },
          '/' : {
            # HTTP verb dispatcher
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.sessions.on': True,
            # Basic Auth
            'tools.auth_basic.on'      : True,
            'tools.auth_basic.realm'   : 'Francis Drake',
            'tools.auth_basic.checkpassword' : clientsCatalog.checkpassword
            # Digest Auth
            #'tools.auth_digest.on'      : True,
            #'tools.auth_digest.realm'   : 'Francis Drake',
            #'tools.auth_digest.get_ha1' : get_ha1,
            #'tools.auth_digest.key'     : 'f565c27146793cfb',
          }
        }
        """
        cherrypy.tree.mount(clientsCatalog, clientsCatalog.service, conf)
        cherrypy.config.update({'server.socket_host':clientsCatalog.clientsCatalogIP})
        cherrypy.config.update({'server.socket_port':clientsCatalog.clientsCatalogPort})
        cherrypy.engine.start()
        """
        while True:
            if clientsCatalog.flagNew:
                clientsCatalog.flagNew=False
                cherrypy.engine.stop()
                cherrypy.server.httpserver=None
                clientsCatalog.catalog.createDict()
                conf = {
                  'global' : {
                    'server.socket_host' : clientsCatalog.clientsCatalogIP,
                    'server.socket_port' : clientsCatalog.clientsCatalogPort,
                    #'server.thread_pool' : 8
                  },
                  '/' : {
                    # HTTP verb dispatcher
                    'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                    'tools.staticdir.root': os.path.abspath(os.getcwd()),
                    'tools.sessions.on': True,
                    # Basic Auth
                    'tools.auth_basic.on'      : True,
                    'tools.auth_basic.realm'   : 'Francis Drake',
                    'tools.auth_basic.checkpassword' : clientsCatalog.checkpassword
                    # Digest Auth
                    #'tools.auth_digest.on'      : True,
                    #'tools.auth_digest.realm'   : 'Francis Drake',
                    #'tools.auth_digest.get_ha1' : get_ha1,
                    #'tools.auth_digest.key'     : 'f565c27146793cfb',
                  }
                }
                
                cherrypy.tree.mount(clientsCatalog, clientsCatalog.service, conf)
                cherrypy.config.update({'server.socket_host':clientsCatalog.clientsCatalogIP})
                cherrypy.config.update({'server.socket_port':clientsCatalog.clientsCatalogPort})
                cherrypy.engine.start()
            time.sleep(1)
            """
        cherrypy.engine.block()
