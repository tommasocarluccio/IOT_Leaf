import cherrypy
import json
import requests
import time
import sys
from etc.adaptor_class import *

class AdaptorREST():
    exposed=True
    def __init__(self,conf_filename):
        self.adaptor=Adaptor(conf_filename)
        self.service=self.adaptor.registerRequest()

    def GET(self,*uri,**params):
        try:
            platform_ID=uri[0]
            #room_ID=uri[1]
            command=uri[1]
            try:
                clients_catalog=self.adaptor.retrieveService('clients_catalog')
                clients_result=requests.get(clients_catalog['url']+"/info/"+platform_ID+"/thingspeak").json()
                channelID=clients_result["channelID"]
            except Exception as e:
                print(e)
                raise cherrypy.HTTPError(500,"Ops! Try later..")

        except:
            raise cherrypy.HTTPError(400,"Check your request and try again!")
        if command=="now":
            thingspeak_url="{}/channels/{}/feeds.json?results=1".format(self.adaptor.thingspeak_url,channelID)
            result=requests.get(thingspeak_url).json()
            print(result)
            return json.dumps(result)
        else:
            raise cherrypy.HTTPError(501, "No operation!")


        
if __name__ == '__main__':
    conf=sys.argv[1]
    adaptorREST=AdaptorREST(conf)
    if adaptorREST.service is not False:
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
            }
        }
        cherrypy.tree.mount(adaptorREST, adaptorREST.service, conf)
        cherrypy.config.update({'server.socket_host': adaptorREST.adaptor.serviceIP})
        cherrypy.config.update({'server.socket_port': adaptorREST.adaptor.servicePort})
        cherrypy.engine.start()

        adaptorREST.adaptor.setup("adaptor")
        cherrypy.engine.block()
