import cherrypy
import json
import os
import sys
import requests
import time
from etc.clients_class import *

class Registration_deployer(object):
    exposed=True
    def __init__(self,filename):
        self.filename=filename
        self.catalog=ClientsCatalog(self.filename)
        self.service=self.catalog.registerRequest()
        #self.flagNew=False

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
                try:
                    profiles_catalog=self.catalog.retrieveService("profiles_catalog")
                    r=requests.put(profiles_catalog['url']+"/insertProfile",json={"platform_ID":params['platformID']}).json()
                    if r['result'] is False:
                        self.catalog.users.removeUser(params['usersID'])
                        self.catalog.platforms.set_value(params['platformID'],"associated",False)
                except:
                    self.catalog.users.removeUser(params['userID'])
                    self.catalog.platforms.set_value(params['platformID'],"associated",False)
                    return open("etc/error.html")
                    
                self.catalog.users.save()
                self.catalog.platforms.save()

                print("User '{}' correctly registered with platform '{}'\n".format(params['userID'],params['platformID']))
                return open("etc/correct_reg.html")
        elif(len(uri))>0 and uri[0]=="login":
            #username=str(cherrypy.request.login)
            username=params['username']
            password=params['password']
            try:
                data=self.catalog.users.login(username,password).copy()
                print(data)
                del data['password']
                return json.dumps(data)
            except:
                raise cherrypy.HTTPError(403,"Login failed")
        elif(len(uri))>0 and uri[0]=="platforms_list":
            #username=str(cherrypy.request.login)
            username=params['username']
            try:
                data=self.catalog.users.find_user(username).copy()
                print(data)
                #del data['password']
                return json.dumps(data['platforms_list'])
            except:
                raise cherrypy.HTTPError(400,"Bad Request!")

        elif(len(uri))>0 and uri[0]=="checkAssociation":
            result=self.catalog.check_association(uri[1])
            return json.dumps({"result":result})

        elif(len(uri))==3 and uri[0]=="info":
            platform=self.catalog.platforms.find_platform(uri[1])
            if platform is not False:
                try:
                    result=json.dumps(platform['specs'][uri[2]])
                    return result
                except:
                    raise cherrypy.HTTPError(400, "Bad request!")
            else:
                raise cherrypy.HTTPError(404, "Platform not found!")
                
                
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
    #get_ha1 = cherrypy.lib.auth_digest.get_ha1_dict_plain(clientsCatalog.catalog.users.userpassdict)
    #clientsCatalog.checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(clientsCatalog.catalog.users.userpassdict)
    if clientsCatalog.service is not False:
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.sessions.on': True
            }
        }

        cherrypy.tree.mount(clientsCatalog, clientsCatalog.service, conf)
        cherrypy.config.update({'server.socket_host':clientsCatalog.catalog.serviceIP})
        cherrypy.config.update({'server.socket_port':clientsCatalog.catalog.servicePort})
        cherrypy.engine.start()

        cherrypy.engine.block()
