import cherrypy
import json
import socket
import sys
import time
import os
import requests

class HUB():
    def __init__(self,db_filename):
        self.db_filename=db_filename
        self.hubContent=json.load(open(self.db_filename,"r"))
        self.service=self.hubContent['service']
        self.serviceCatalogAddress=self.hubContent['service_catalog']
        self.hub_ID=self.hubContent['hub_ID']
        self.rooms=self.hubContent['rooms']

    def retrieveBroker(self):
        print("Retrieving broker information...")
        try:
            requestBroker=requests.get(self.serviceCatalogAddress+'/broker').json()
            IP=requestBroker.get('IP_address')
            msg={"IP_address":IP}
            self.hubContent["broker"].append(msg)
            print("Broker info obtained.")
        except IndexError as e:
            print("Broker info not obtained.")
            
    def setup(self):
        print("Connecting...")
        try:
            requestResourcesCatalog=requests.get(self.serviceCatalogAddress+'/resource_catalog').json()
            self.hubContent['resource_catalog']=requestResourcesCatalog['url']
            json_body={"platform_ID":self.hub_ID,"rooms":self.rooms}
            r=requests.put(self.hubContent['resource_catalog']+'/insertPlatform',json=json_body).json()
            if r["result"]:
                print("Connection performed")
                return True
            else:
                print("Setting failed")
                return False
        except:
            print("Connection failed.")
            return False


    def retrieveInfo(self,parameter):
        try:
            result= self.hubContent[parameter]
        except:
            result=False
        return result

class HUB_REST():
    exposed=True
    def __init__(self,db_filename,IP):
        self.hubCatalog=HUB(db_filename)
        self.IP=IP
        self.port=self.hubCatalog.hubContent["IP_port"]

    def GET(self, *uri):
        if len(uri)>0:
            parameter=uri[0]
            info=self.hubCatalog.retrieveInfo(parameter)
            if info is not False:
                output=info
            else:
                raise cherrypy.HTTPError(404,"Information Not found")

        else:
            output=self.hubCatalog.retrieveInfo('description')
        return json.dumps(output) 

if __name__ == '__main__':
    db=sys.argv[1]
    IP=socket.gethostbyname(socket.gethostname())
    hub=HUB_REST(db,IP)
    hub.hubCatalog.retrieveBroker()
    time.sleep(0.5)
    if hub.hubCatalog.setup():
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
            }
        }
        cherrypy.tree.mount(hub, hub.hubCatalog.service, conf)
        cherrypy.config.update({'server.socket_host': hub.IP})
        cherrypy.config.update({'server.socket_port': hub.port})
        cherrypy.engine.start()
        while True:
            time.sleep(1)
        cherrypy.engine.block()

