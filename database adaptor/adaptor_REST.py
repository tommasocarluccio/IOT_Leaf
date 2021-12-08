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
