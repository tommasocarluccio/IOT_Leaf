from collections import defaultdict
import cherrypy
import json
import requests
import time
import sys
from datetime import datetime
from etc.grafana_class import *

class GrafanaREST():
    exposed=True
    def __init__(self,conf_filename):
        self.grafana=Grafana(conf_filename)
        self.service=self.grafana.registerRequest()        

    def GET(self, *uri):
        
        try:
            platform_ID=uri[0]
            room_ID=uri[1]
            command=uri[2]            
        except:
            raise cherrypy.HTTPError(400,"Check your request and try again!") 
        if command=='dashboardURL':
            log=self.grafana.getDashboardURL(platform_ID, room_ID)
            if log is not False:
                return log
            else:
                raise cherrypy.HTTPError(404, "Resource not found!")
        else:
            raise cherrypy.HTTPError(501, "No operation!") 

    def POST(self, *uri):
        
        try:
            platform_ID=uri[0]
            room_ID=uri[1]
            command=uri[2]            
        except:
            raise cherrypy.HTTPError(400,"Check your request and try again!")    
        
        if command=='createDashboard':
            log=self.grafana.createDashboard(platform_ID, room_ID)
            if log==True:
                print("Successfully created dashboard")
        
        else:
            raise cherrypy.HTTPError(501, "No operation!")

    def DELETE(self, *uri):
        
        try:
            platform_ID=uri[0]
            room_ID=uri[1]
            command=uri[2]
            org_key=uri[3]            
        except:
            raise cherrypy.HTTPError(400,"Check your request and try again!")    
        
        if command=='deleteDashboard':
            log=self.grafana.deleteDashboard(platform_ID, room_ID, org_key)
            if log==True:
                print("Successfully deleted dashboard")
        
        else:
            raise cherrypy.HTTPError(501, "No operation!")

if __name__ == '__main__':
    conf=sys.argv[1]
    grafanaREST=GrafanaREST(conf)
    if grafanaREST.service is not False:
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
            }
        }
        cherrypy.tree.mount(grafanaREST, grafanaREST.service, conf)
        cherrypy.config.update({'server.socket_host': grafanaREST.grafana.serviceIP})
        cherrypy.config.update({'server.socket_port': grafanaREST.grafana.servicePort})
        cherrypy.engine.start()

        cherrypy.engine.block()
