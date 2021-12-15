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
                    r=requests.put(profiles_catalog['url']+"/insertProfile",json={"platform_ID":params['platformID']})
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
                raise cherrypy.HTTPError("401 Login failed")
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

        elif(len(uri))>0 and uri[0]=="tokens":
            result=self.catalog.platforms.content['tokens']
            return json.dumps(result)

        elif(len(uri))>0 and uri[0]=="temp_tokens":
            result=json.load(open('database/temp_token.json',"r"))
            return json.dumps(result)

        elif (len(uri))>0 and uri[0]=="associated_rooms":
            platform=self.catalog.platforms.find_platform(uri[1])
            if platform is not False:
                try:
                    log=platform['specs'][uri[2]]
                    output=[]
                    for i in log:
                        output.append(i['room'])
                    return json.dumps(output)
                except:
                    raise cherrypy.HTTPError(400, "Bad request!")
            else:
                raise cherrypy.HTTPError("404 Platform not found!")


        elif(len(uri))==4 and uri[0]=="info":
            platform=self.catalog.platforms.find_platform(uri[1])
            if platform is not False:
                try:
                    result=json.dumps(platform['specs'][uri[3]])
                    return result
                except:
                    raise cherrypy.HTTPError(400, "Bad request!")
            else:
                raise cherrypy.HTTPError(404, "Platform not found!")
                
                
        else:
            raise cherrypy.HTTPError("501 No operation!")
            
    def PUT(self,*uri):
        command=str(uri[0])
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        if command=="newPlatform":
            user=self.catalog.users.find_user(json_body['username'])
            if not self.catalog.check_association(json_body['platformID']) and user is not False:
                profiles_catalog=self.catalog.retrieveService("profiles_catalog")
                r=requests.put(profiles_catalog['url']+"/insertProfile",json={"platform_ID":json_body['platformID']})
                if r.status_code==200:
                    user['platforms_list'].append(json_body['platformID'])
                    self.catalog.platforms.set_value(params['platformID'],"associated",True)
                    self.catalog.users.save()
                    self.catalog.platforms.save()
                    print("Platform {} correctly associated.".format(platform_ID))
                        
                else:
                    return r
            else:
                raise cherrypy.HTTPError("409 Already exists!")

        if command=="newRoom":
            output=self.catalog.platforms.associate_room_thingspeak(json_body['platformID'],json_body['roomID'])
            if output is not False:
                self.catalog.platforms.save()
                print("{} - {}".format(json_body['platformID'],json_body['roomID']))
                print(output)
                return json.dumps({'msg':output})
            else:
                raise cherrypy.HTTPError("404 Platform not found!")
        else:
            raise cherrypy.HTTPError("501 No operation!")

    def DELETE(self,*uri):
        command=str(uri[0])
        if command=='removePlatform':
            try:
                username=uri[1]
                platform_ID=uri[2]
            except:
                raise cherrypy.HTTPError("400 Missing parameters!")
            outputFlag=self.catalog.users.removePlatform(username,platform_ID)
            if outputFlag:
                output="Platform '{}' removed".format(platform_ID)
                print(output)
                self.catalog.platforms.set_value(platform_ID,"associated",False)
                self.catalog.platforms.remove_all_rooms(platform_ID)
                self.catalog.users.save()
                self.catalog.platforms.save()
            else:
                output="Platform '{}' not found ".format(platform_ID)
                print(output)
                raise cherrypy.HTTPError("404 Resource not found")

        if command=='removeRoom':
            try:
                username=uri[1]
                platform_ID=uri[2]
                room_ID=uri[3]
            except:
                raise cherrypy.HTTPError("400 Missing parameters!")
            if self.catalog.users.find_user(username) and platform_ID in self.catalog.users.find_user(username)["platforms_list"]:
                outputFlag=self.catalog.platforms.removeRoom(platform_ID,room_ID)
                if outputFlag:
                    output="Platform '{}' - room '{}' removed".format(platform_ID,room_ID)
                    print(output)
                    self.catalog.platforms.save()
            else:
                raise cherrypy.HTTPError("404 Resource not found")

        elif command=='removeUser':
            username=uri[1]
            outputFlag=self.catalog.users.removeUser(username)
            if outputFlag:
                output="User '{}' removed".format(username)
                print(output)
                self.catalog.users.save()
            else:
                raise cherrypy.HTTPError("404 User not found")
        
        else:
            raise cherrypy.HTTPError("501 No operation!")

    
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
