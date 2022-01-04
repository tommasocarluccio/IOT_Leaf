import cherrypy
import json
import requests
import time
import datetime
import sys
import threading
from etc.serverClass import *

class ResourcesServerREST(object):
    exposed=True
    def __init__(self,conf_filename,db_filename):
        self.catalog=ResourceService(conf_filename,db_filename)
        self.service=self.catalog.registerRequest()            

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
                else:
                    raise cherrypy.HTTPError("409 Platform Not valid")
                    
            self.catalog.insertRoom(platform_ID,room_ID,json_body)
            saveFlag=True
        elif command=="insertDevice":
            platform_ID=uri[1]
            room_ID=uri[2]
            device=self.catalog.insertDevice(platform_ID,room_ID,json_body)
            if device is False:
                raise cherrypy.HTTPError(404, "Resource not found!")
            else:
                saveFlag=True
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag:
            self.catalog.save()

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
                    if removedDevice:
                        output="Platform '{}' - Room '{}' - Device '{}' removed".format(platform_ID,room_ID,device_ID)
                        self.catalog.dateUpdate(self.catalog.retrieveRoomInfo(platform_ID,room_ID))
                        saveFlag=True
                    else:
                        output="Platform '{}'- Room '{}' - Device '{}' not found ".format(platform_ID,room_ID,device_ID)
                        raise cherrypy.HTTPError(404, "Resource not found!")
                else:

                    removedRoom=self.catalog.removeRoom(platform_ID,room_ID)
                    if removedRoom:

                        output="Platform '{}' - Room '{}' removed".format(platform_ID,room_ID)
                        saveFlag=True
                    else:
                        output="Platform '{}'- Room '{}' not found ".format(platform_ID,room_ID)
                        raise cherrypy.HTTPError(404, "Resource not found!")

            else:
                removedPlatform=self.catalog.removePlatform(platform_ID) 
                if removedPlatform:
                    output="Platform '{}' removed".format(platform_ID)
                    saveFlag=True
                else:
                    output="Platform '{}' not found ".format(platform_ID)
                    raise cherrypy.HTTPError(404, "Resource not found!")
        else:
            raise cherrypy.HTTPError(501, "No operation!")
        if saveFlag:
            self.catalog.save()
        print(output)
        return{"result":saveFlag}

class InactiveThread(threading.Thread):

    def __init__(self, ThreadID,catalog):
        threading.Thread.__init__(self)
        self.ThreadID = ThreadID
        self.catalog=catalog

    def run(self):
        while True:
            bot_url=self.catalog.retrieveService("telegram_bot")
            for platform in self.catalog.db_content['platforms_list']:
                for room in platform['rooms']:
                    devices=room['devices']
                    devicesCatalog=DevicesCatalog(devices)
                    dev_list=devicesCatalog.removeInactive(self.catalog.delta)
                    for dev in dev_list:
                        msg={"parameter":dev,"status":"REMOVED","tip":None}
                        requests.post(bot_url+'/warning/'+platform_ID+'/'+room_ID, json=msg)
            self.catalog.save()
            time.sleep(self.catalog.delta)

if __name__ == '__main__':
    conf=sys.argv[1]
    db=sys.argv[2]
    server=ResourcesServerREST(conf,db)
    thread1=InactiveThread(1,server.catalog)
    thread1.start()
    time.sleep(1)
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
    #cherrypy.engine.block()