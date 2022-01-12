import cherrypy
import json
import requests
import time
import sys
from etc.profiles_class import ProfilesCatalog

class catalogREST():
    exposed=True
    def __init__(self,conf_filename,db_filename):
        self.catalog=ProfilesCatalog(conf_filename,db_filename)
        self.service=self.catalog.registerRequest()
        
    def GET(self,*uri):
        uriLen=len(uri)
        output=False
        if uriLen!=0:
            profile= self.catalog.retrieveProfileInfo(uri[0])
            if profile is not False:
                if uriLen>1:
                    profileInfo= self.catalog.retrieveProfileParameter(uri[0],uri[1])
                    output=profileInfo
                    if uriLen>2:
                        if str(uri[2])=='rooms_list':
                            roomInfo=self.catalog.retrieveRoomList(profileInfo)
                        else:
                            roomInfo=self.catalog.retrieveRoomInfo(profileInfo,uri[2])
                        if uriLen>3:
                            try:
                                output=roomInfo[uri[3]]
                                if uriLen>4:
                                    try:
                                        output=roomInfo["preferences"][uri[4]]
                                    except Exception as e:
                                        print(e)
                                        output=False
                            except:
                                output=False
                        else:
                            output=roomInfo

                else:
                    output=profile

            if not output:
                raise cherrypy.HTTPError(404,"Information Not found")

        else:
            output=self.catalog.conf_content['description']

        return json.dumps(output) 

    def PUT(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        saveFlag=False
        msg={"msg":None}
        if command=='insertProfile':
            try:
                platform_ID=json_body['platform_ID']
                platform_name=json_body['platform_ID']
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")
            newProfile=self.catalog.insertProfile(platform_ID,platform_name)
            if newProfile:
                output="Profile '{}' has been added to Profiles Database".format(platform_ID)
                msg['msg']=output
                saveFlag=True
            else:
                output="'{}' already exists!".format(platform_ID)
                raise cherrypy.HTTPError("409 Resource already exists!")
        #from bot
        elif command=='insertRoom':
            try:
                platform_ID=uri[1]
                room_name=json_body['room_name']
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")

            newRoom=self.catalog.insertRoom(platform_ID,room_name)
            if newRoom is not False:
                output="Room '{}' has been added to platform '{}'".format(room_name,platform_ID)
                clients_service=self.catalog.retrieveService('clients_catalog')
                json_msg={"platformID":platform_ID,"roomID":newRoom.room_info['room_ID']}
                thingspeak_association=requests.put(clients_service['url']+"/newRoom",json=json_msg)
                if thingspeak_association.status_code==200:
                    output=output+". "+thingspeak_association.json()['msg']
                    msg['msg']=output
                    saveFlag=True
                else:
                    self.catalog.removeRoom(platform_ID,room_ID)
                    return thingspeak_association
            else:
                output="Room '{}' cannot be added to platform '{}'".format(room_name,platform_ID)
                raise cherrypy.HTTPError("400 Platform not found")
                
        #from physical platform        
        elif command=='associateRoom':
            try:
                platform_ID=uri[1]
                timestamp=json_body['timestamp']
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")
            associatedRoom=self.catalog.associateRoom(platform_ID,timestamp)
            if associatedRoom is not False:
                output="Room '{}' has been associated in platform '{}'".format(associatedRoom['preferences']['room_name'],platform_ID)
                msg['msg']={"room_ID": associatedRoom['room_ID'], "room_name": associatedRoom['preferences']['room_name'],"connection_timestamp":associatedRoom['connection_timestamp']}
                saveFlag=True
            else:
                output="Association failed in platform '{}' or already performed.".format(platform_ID)
                raise cherrypy.HTTPError("409 "+output)

        else:
            raise cherrypy.HTTPError("501 No operation!")
        
        if saveFlag:
            self.catalog.save()
        print(output)
        return json.dumps(msg)
		
    def POST(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        if command=='setParameter':
            try:
                platform_ID=uri[1]
                parameter=json_body['parameter']
                parameter_value=json_body['parameter_value']
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")
            newSetting=self.catalog.setParameter(platform_ID,parameter,parameter_value)
            if newSetting:
                output="Platform '{}': {} is now {}".format(platform_ID, parameter,parameter_value)
                self.catalog.save()
            else:
                output="Platform '{}': Can't change {} ".format(platform_ID, parameter)
                raise cherrypy.HTTPError(404, "No resource available!")
            print(output)
            return json.dumps({"msg":output})

        elif command=='setRoomParameter':
            try:
                platform_ID=uri[1]
                room_ID=uri[2]
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")

            newSetting=self.catalog.setRoomParameter(platform_ID,room_ID,json_body)
            if newSetting:
                output="Platform '{}' - Room '{}': parameter updated".format(platform_ID,room_ID)
                self.catalog.save()
            else:
                output="Platform '{}' Room '{}': Can't change parameter".format(platform_ID, room_ID)
                raise cherrypy.HTTPError(404, "No resource available!")
            print(output)
            return json.dumps({"msg":output})

        else:
            raise cherrypy.HTTPError(501, "No operation!")

    def DELETE(self,*uri):
        command=str(uri[0])
        try:
            clients_service=self.catalog.retrieveService('clients_catalog')
        except:
            raise cherrypy.HTTPError("503 Can't perform the request now...")
        if command=='removeProfile':
            try:
                username=uri[1]
                platform_ID=uri[2]
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")
            r_client=requests.delete(clients_service['url']+"/removePlatform/"+username+"/"+platform_ID)
            if r_client.status_code==200:
                removedProfile=self.catalog.removeProfile(platform_ID)
                if removedProfile:
                    output="Profile '{}' removed".format(platform_ID)
                    resource_service=self.catalog.retrieveService('resource_catalog')
                    try:
                        requests.delete(resource_service['url']+"/"+platform_ID)
                    except:
                        pass
                    self.catalog.save()
                    result={"msg":output}
                    return json.dumps(result)
                else:
                    output="Platform '{}' not found ".format(platform_ID)
                    raise cherrypy.HTTPError("400 Resource not found.")
                print(output)
            else:
                raise cherrypy.HTTPError("{} {}".format(str(r_client.status_code),str(r_client.reason)))

        elif command=='removeRoom':
            try:
                username=uri[1]
                platform_ID=uri[2]
                room_ID=uri[3]
            except:
                raise cherrypy.HTTPError("400 Bad Request! You need to specify parameters")

            r_client=requests.delete(clients_service['url']+"/removeRoom/"+username+"/"+platform_ID+"/"+room_ID)
            if r_client.status_code==200:
                removedRoom=self.catalog.removeRoom(platform_ID,room_ID)
                if removedRoom:
                    self.catalog.save()
                    output="Room '{}' removed from platform '{}'. ".format(room_ID,platform_ID)
                    resource_service=self.catalog.retrieveService('resource_catalog')
                    try:
                        requests.delete(resource_service['url']+"/"+platform_ID+"/"+room_ID)
                    except:
                        pass
                    self.catalog.save()
                    result={"msg":output}
                    return json.dumps(result)
                else:
                    output="Can't remove room '{}' from platform '{}'. ".format(room_ID,platform_ID)
                    raise cherrypy.HTTPError("404 Resource not found")
                print(output)
            else:
                raise cherrypy.HTTPError("{} {}".format(str(r_client.status_code),str(r_client.reason)))
        else:
            raise cherrypy.HTTPError("501 No operation!")
   
if __name__ == '__main__':
    conf=sys.argv[1]
    db=sys.argv[2]
    ProfilesCatalog=catalogREST(conf,db)
    if ProfilesCatalog.service is not False:
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
            }
        }
        cherrypy.tree.mount(ProfilesCatalog, ProfilesCatalog.service, conf)
        cherrypy.config.update({'server.socket_host': ProfilesCatalog.catalog.serviceIP})
        cherrypy.config.update({'server.socket_port': ProfilesCatalog.catalog.servicePort})
        cherrypy.engine.start()
        cherrypy.engine.block()
