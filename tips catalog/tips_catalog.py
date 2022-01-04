import cherrypy
import json
import requests
import sys
from etc.tips_class import TipsHandler
from etc.generic_service import *

class TipsREST(Generic_Service):
    exposed=True
    def __init__(self,filename):
        Generic_Service.__init__(self,filename)
        self.service=self.registerRequest()
        self.catalog=TipsHandler()

    def GET(self,*uri):
        if uri[0]=="tip":
            if len(uri)>1:
                try:
                    return self.catalog.param_tip(uri[1],uri[2].lower())
                except:
                    raise cherrypy.HTTPError(404,"Resource not found!")
            else:
                return self.catalog.new_tip()
        else:
            raise cherrypy.HTTPError("501 No operation!")


   
if __name__ == '__main__':
    conf=sys.argv[1]
    catalog=TipsREST(conf)
    if catalog.service is not False:
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
            }
        }
        cherrypy.tree.mount(catalog, catalog.service, conf)
        cherrypy.config.update({'server.socket_host': catalog.serviceIP})
        cherrypy.config.update({'server.socket_port': catalog.servicePort})
        cherrypy.engine.start()
        cherrypy.engine.block()
