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
        elif command=='station':
            thingspeak_url="{}/channels/{}/feeds.json?metadata=true".format(self.adaptor.thingspeak_url,channelID)
            result=requests.get(thingspeak_url).json()
            print(result)
            return json.dumps(result['channel']['metadata'])
        else:
            raise cherrypy.HTTPError(501, "No operation!")
    
    def POST(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        platform_ID=uri[0]
        room_ID=uri[1]
        command=str(uri[2])
        if command=='check_warning':
            data=json_body['data']
            average=self.adaptor.get_average_values(platform_ID, room_ID, data)
            if self.adaptor.check_thresholds(platform_ID, room_ID, data, average)=="low":
                print("Warning low value")
                warning_body={
                    "parameter":data['parameter'],
                    "value":data['value'],
                    "alert":"is too low"
                }
                bot_url=' '
                requests.post(bot_url+'/'+platform_ID+'/'+room_ID+'/warning', json=warning_body)
            elif self.adaptor.check_thresholds(platform_ID, room_ID, data, average)=="high":
                warning_body={
                    "parameter":data['parameter'],
                    "value":data['value'],
                    "alert":"is too high"
                }
                print("Warning high value")
                requests.post(bot_url+'/'+platform_ID+'/'+room_ID+'/warning', json=warning_body)
            else:
                print("No warning")

    def PUT(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        print(json_body)
        try:
            platform_ID=uri[0]
            #room_ID=uri[1]
            command=uri[1]
            try:
                clients_catalog=self.adaptor.retrieveService('clients_catalog')
                clients_result=requests.get(clients_catalog['url']+"/info/"+platform_ID+"/thingspeak").json()
                channelID=clients_result["channelID"]
                put_key=clients_result["put_key"]
            except Exception as e:
                print(e)
                raise cherrypy.HTTPError(500,"Ops! Try later..")

        except:
            raise cherrypy.HTTPError(400,"Check your request and try again!")    
        
        if command=='uploadLocation':
            thingspeak_url="{}/channels/{}.json".format(self.adaptor.thingspeak_url,channelID)
            headers={"content-type":"application/x-www-form-urlencoded"}
            json_body['api_key']=put_key
            result=requests.put(thingspeak_url, headers=headers, data=json_body)
            print(result.json())
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
