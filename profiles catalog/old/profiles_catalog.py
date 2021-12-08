import cherrypy
import json
import requests
import time
import sys
from profiles_class import ProfilesCatalog

class catalogREST():
    exposed=True
    def __init__(self,conf_filename,db_filename):
        self.catalog=ProfilesCatalog(conf_filename,db_filename)
        self.service=self.catalog.registerRequest()
        
    def GET(self,*uri):
        uriLen=len(uri)
        if uriLen!=0:
            profile= self.catalog.retrieveProfileInfo(uri[0])
            if profile is not False:
                if uriLen>1:
                    if uri[1]=="preferences":
                        for room in profile["preferences"]:
                            try:
                                devices=self.serverRequest(uri[0],room["room_ID"],"devices")
                                self.catalog.createDevicesList(uri[0],room["room_ID"],devices)
                            except:
                                pass
                    profileInfo= self.catalog.retrieveProfileParameter(uri[0],uri[1])
                    if uriLen==3:
                        try:
                            pos=self.catalog.findRoomPos(profileInfo,uri[2])
                            profileInfo=profileInfo[pos]
                        except:
                            pass
                    if profileInfo is not False:
                        output=profileInfo
                    else:
                        output=profile.get(uri[1])
                else:
                    output=profile
            else:
                output=self.catalog.profilesContent.get(uri[0])
            if output==None:
                raise cherrypy.HTTPError(404,"Information Not found")

        else:
            output=self.catalog.conf_content['description']

        return json.dumps(output) 

    def PUT(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        ack=False
        saveFlag=False
        if command=='insertProfile':
            platform_ID=json_body['platform_ID']
            platform_name=json_body['platform_ID']
            newProfile=self.catalog.insertProfile(platform_ID,platform_name)
            
            if newProfile==True:
                output="Profile '{}' has been added to Profiles Database".format(platform_ID)
                saveFlag=True
                ack=True
            else:
                output="'{}' already exists!".format(platform_ID)
                ack=False
        #from bot
        elif command=='insertRoom':
            platform_ID=uri[1]
            room_name=json_body['room_name']
            newRoomFlag=self.catalog.insertRoom(platform_ID,json_body)
            if newRoomFlag==True:
                output="Room '{}' has been added to platform '{}'".format(room_name,platform_ID)
                saveFlag=True
                ack=newRoomFlag
            else:
                output="Room '{}' cannot be added to platform '{}'".format(room_name,platform_ID)
                
        elif command=='associateRoom':
            platform_ID=uri[1]
            associatedRoomFlag,associatedRoom=self.catalog.associateRoom(platform_ID,json_body['timestamp'])
            if associatedRoomFlag==True:
                output="Room '{}' has been assoicated in platform '{}'".format(associatedRoom['room_name'],platform_ID)
                ack=associatedRoom
                saveFlag=True
            else:
                output="Association failed in platform '{}'".format(platform_ID)


        else:
            raise cherrypy.HTTPError(501, "No operation!")
        
        if saveFlag==True:
            self.catalog.save()
        print(output)
        return json.dumps({"result":ack})
		

    def POST(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        if command=='setParameter':
            platform_ID=uri[1]
            parameter=json_body['parameter']
            parameter_value=json_body['parameter_value']
            newSetting=self.catalog.setParameter(platform_ID,parameter,parameter_value)
            if newSetting==True:
                output="Platform '{}': {} is now {}".format(platform_ID, parameter,parameter_value)
                self.catalog.save()
            else:
                output="Platform '{}': Can't change {} ".format(platform_ID, parameter)
            print(output)
        elif command=='setRoomParameter':
            platform_ID=uri[1]
            room_ID=uri[2]
            parameter=json_body['parameter']
            parameter_value=json_body['parameter_value']
            newSetting=self.catalog.setRoomParameter(platform_ID,room_ID,parameter,parameter_value)
            if newSetting==True:
                output="Platform '{}' - Room '{}': {} is now {}".format(platform_ID,room_ID, parameter,parameter_value)
                self.catalog.save()
            else:
                output="Platform '{}' Room '{}': Can't change {} ".format(platform_ID, room_ID,parameter)
            print(output)

            
        else:
            raise cherrypy.HTTPError(501, "No operation!")

    def DELETE(self,*uri):
        command=str(uri[0])
        if command=='removeProfile':
            username=uri[1]
            platform_ID=uri[2]
            try:
                clients_service=self.catalog.retrieveService('clients_catalog')
                r=requests.delete(clients_service['url']+"/removePlatform/"+username+"/"+platform_ID).json()
                print(r)
                if r['result']:
                    removedProfile=self.catalog.removeProfile(platform_ID)
                    if removedProfile:
                        output="Profile '{}' removed".format(platform_ID)
                        self.catalog.save()
                        result={"result":True}
                    else:
                        output="Platform '{}' not found ".format(platform_ID)
                        result={"result":False}
                        
                else:
                    output="Operation failed."
                    result={"result":False} 
            except Exception as e:
                print(e)
                output="Communication error."
                result={"result":False} 
            print(output)
            return json.dumps(result)
        elif command=='removeRoom':
            platform_ID=uri[1]
            room_ID=uri[2]
            removedRoom=self.catalog.removeRoom(platform_ID,room_ID)
            if removedRoom==True:
                """
                try:
                    self.serverDelete(platform_ID+'/'+room_ID)
                    pass
                except:
                    pass
                """
                self.catalog.save()
                output="Room '{}' from platform '{}' removed".format(room_ID,platform_ID)
                #self.catalog.save()
                result={"result":True}
            else:
                output="Room '{}' from platform '{}' ".format(room_ID,platform_ID)
                result={"result":False}
            print(output)
            return json.dumps(result)
            
            
            
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        

        
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
        """
        while True:
            influx_IP,influx_port,influx_service=catalog.retrieveService('influx_db')
            for platform in catalog.catalog.profilesContent['profiles']:
                platform_ID=platform.get("platform_ID")
                location=platform.get("location")
                url=catalog.catalog.buildWeatherURL(location)
                try:
                    r=requests.get(url).json()
                
                    body=catalog.catalog.createBody(platform_ID,location,r)
                    clientDB=InfluxDBClient(influx_IP,influx_port,'root','root',platform_ID)
                    try:
                        clientDB.write_points(body)
                    except:
                        pass
                except:
                    pass
                time.sleep(5)
                
            
            time.sleep(catalog.catalog.delta)
        """
        cherrypy.engine.block()