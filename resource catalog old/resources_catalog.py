import cherrypy
import json
import requests
import time
import datetime
import sys
from etc.serverClass import *

class ResourcesServerREST(object):
    exposed=True
    def __init__(self,conf_filename,db_filename):
        self.catalog=ResourceService(conf_filename,db_filename)
        self.service=self.catalog.registerRequest()
    
    def setup(self,clientID):
        try:
            broker=requests.get(self.catalog.serviceCatalogAddress+'/broker').json()
            broker_IP=broker.get('IP_address')
            broker_port=broker.get('port')
            self.catalog.subscriber=DataCollector(clientID,broker_IP,broker_port,self.catalog)
            self.catalog.subscriber.run()
            for platform in self.catalog.retrievePlatformsList():
                server.catalog.subscriber.follow(platform+'/#')
        except Exception as e:
            print(e)
            print("MQTT Subscriber not created")
            

    def GET(self,*uri,**params):
        uriLen=len(uri)
        if uriLen!=0:
            info=uri[0]
            if info=="platformsList":
                output=self.catalog.retrievePlatformsList()
            else:    
                platform= self.catalog.retrievePlatform(info)
                if platform is not False:
                    if uriLen>1:
                        roomInfo= self.catalog.retrieveRoomInfo(info,uri[1])
                        if roomInfo is not False:
                            if uriLen>2:
                                deviceInfo=self.catalog.retrieveDeviceInfo(info,uri[1],uri[2])
                                if deviceInfo is not False:
                                    if uriLen>3:
                                        output=deviceInfo.get(uri[3])
                                    elif len(params)!=0:
                                        parameter=str(params['parameter'])
                                        parameterInfo=self.catalog.retrieveParameterInfo(info,uri[1],uri[2],parameter)
                                        if parameterInfo is False:
                                            output=None
                                        else:
                                            output=parameterInfo
                                    else:
                                        output=deviceInfo

                                else:
                                    output=roomInfo.get(uri[2])

                            elif len(params)!=0:
                                parameter=str(params['parameter'])
                                parameterInfo=self.catalog.findParameter(info,uri[1],parameter)
                                if parameterInfo is False:
                                    output=None
                                else:
                                    output=parameterInfo

                            else:
                                output=roomInfo
                        else:
                            output=platform.get(uri[1])
                    else:
                        output=platform
                else:
                    output=self.catalog.db_content.get(info)
            if output==None:
                raise cherrypy.HTTPError(404,"Information Not found")

        else:
            output=self.catalog.db_content['description']

        return json.dumps(output) 

    def PUT(self,*uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        command=str(uri[0])
        saveFlag=False
        """
        if command=='insertPlatform':
            requestClients=requests.get(self.catalog.serviceCatalogAddress+"/clients_catalog").json()
            platform_ID=json_body['platform_ID']
            if(requests.get(requestClients['url']+'/checkAssociation/'+platform_ID).json()):
                rooms=[]
                newPlatform=self.catalog.insertPlatform(platform_ID,rooms)
                if newPlatform==True:
                    output="Platform '{}' has been added to Resource Catalog\n".format(platform_ID)
                    res={"result":True}
                    saveFlag=True
                        
                else:
                    output="'{}' already exists!".format(platform_ID)
                    res={"result":True}
                    #platform=self.catalog.retrievePlatform(platform_ID)
                    #platform['local_IP']=json_body['local_IP']
            else:
                output="'{}' cannot be connected".format(platform_ID)
                res={"result":False}
        """    
        if command=='insertRoom':
            platform_ID=uri[1]
            room_ID=json_body['room_ID']
            room_name=json_body['room_name']
            platformFlag=self.catalog.retrievePlatform(platform_ID)
            if platformFlag is False:
                requestClients=requests.get(self.catalog.serviceCatalogAddress+"/clients_catalog").json()
                if(requests.get(requestClients['url']+'/checkAssociation/'+platform_ID).json()["result"]):
                    rooms=[]
                    newPlatform=self.catalog.insertPlatform(platform_ID,rooms)
                    self.catalog.subscriber.follow(platform_ID+'/#')
                else:
                    res={"result":False}
                    raise cherrypy.HTTPError(400,"Platform Not valid")
                    
            room=self.catalog.insertRoom(platform_ID,room_ID,json_body)
            if room is False:
                output="Platform '{}' - Room '{}' already exists. Resetted...".format(platform_ID,room_ID)
            else:
                output="Platform '{}' - Room '{}' has been added to Server".format(platform_ID, room_ID)
            res={"result":True}
            saveFlag=True

        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag:
            self.catalog.save()
        if output is not None:
            print(output)
        return json.dumps(res)

    def DELETE(self,*uri):
        saveFlag=False
        uriLen=len(uri)
        if uriLen>0:
            platform_ID=uri[0]
            if uriLen>1:
                room_ID=uri[1]
                if uriLen>2:
                    device_ID=uri[2]
                    removedDevice=self.catalog.removeDevice(platform_ID,room_ID,device_ID)
                    if removedDevice==True:
                        output="Platform '{}' - Room '{}' - Device '{}' removed".format(platform_ID,room_ID,device_ID)
                        self.catalog.dateUpdate(self.catalog.retrieveRoomInfo(platform_ID,room_ID))
                        saveFlag=True
                    else:
                        output="Platform '{}'- Room '{}' - Device '{}' not found ".format(platform_ID,room_ID,device_ID)
                else:

                    removedRoom=self.catalog.removeRoom(platform_ID,room_ID)
                    if removedRoom==True:

                        output="Platform '{}' - Room '{}' removed".format(platform_ID,room_ID)
                        saveFlag=True
                    else:
                        output="Platform '{}'- Room '{}' not found ".format(platform_ID,room_ID)

            else:
                removedPlatform=self.catalog.removePlatform(platform_ID) 
                if removedPlatform==True:
                    output="Platform '{}' removed".format(platform_ID)
                    saveFlag=True
                else:
                    output="Platform '{}' not found ".format(platform_ID)
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag:
            self.catalog.save()
        print(output)
        return{"result":saveFlag}


if __name__ == '__main__':
    conf=sys.argv[1]
    db=sys.argv[2]
    server=ResourcesServerREST(conf,db)
    server.setup("Resourse_subscriber")
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(server, server.service, conf)
    cherrypy.config.update({'server.socket_host': server.catalog.serviceIP})
    cherrypy.config.update({'server.socket_port': server.catalog.servicePort})
    cherrypy.engine.start()
    cherrypy.engine.block()

