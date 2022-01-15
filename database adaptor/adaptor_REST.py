from collections import defaultdict
import cherrypy
import json
import requests
import time
import sys
from datetime import datetime
from etc.adaptor_class import *

class AdaptorREST():
    exposed=True
    def __init__(self,conf_filename):
        self.adaptor=Adaptor(conf_filename)
        self.service=self.adaptor.registerRequest()

    def GET(self,*uri,**params):
        try:
            platform_ID=uri[0]
            room_ID=uri[1]
            command=uri[2]
            try:
                clients_catalog=self.adaptor.retrieveService('clients_catalog')
                clients_result=requests.get(clients_catalog['url']+"/info/"+platform_ID+"/thingspeak").json()
                client=next((item for item in clients_result if item["room"] == room_ID), False)
                channelID=client["channelID"]
                fields=client['fields']
            except Exception as e:
                print(e)
                raise cherrypy.HTTPError(500,"Ops! Try later..")

        except:
            raise cherrypy.HTTPError(400,"Check your request and try again!")
            
        if command=="now":
            thingspeak_url="{}/channels/{}/feeds/last.json".format(self.adaptor.thingspeak_url,channelID)
            result=requests.get(thingspeak_url).json()
            output=defaultdict(list)
            for d in (fields, result):
                for key, value in d.items():
                    output[key].append(value)
            #print(output)
            return json.dumps(output)

        elif command=='station':
            thingspeak_url="{}/channels/{}/feeds.json?metadata=true".format(self.adaptor.thingspeak_url,channelID)
            result=requests.get(thingspeak_url).json()
            return json.dumps(result['channel']['metadata'])

        elif command=="check_warning":
            parameter=str(params['parameter'])
            wnd_size=str(str(params['time']))
            thingspeak_url="{}/channels/{}/feeds.json?average={}".format(self.adaptor.thingspeak_url, channelID,wnd_size)
            for key,value in fields.items():
                if value==parameter:
                    break

            average_data=requests.get(thingspeak_url).json()
            return json.dumps(float(average_data['feeds'][-1][key]))
        
        elif command=="period":

            date_start = uri[3]
            date_end = uri[4]
            start = date_start.split('_')
            date_start = ' '.join(start)
            end = date_end.split('_')
            date_end = ' '.join(end)

            date_start = datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S")
            date_end = datetime.strptime(date_end, "%Y-%m-%d %H:%M:%S")

            # format dates
            date_now = date_start.strftime("%Y-%m-%d %H:%M:%S").split()
            date_last = date_end.strftime("%Y-%m-%d %H:%M:%S").split()
            end_date = '%20'.join(date_now)
            start_date = '%20'.join(date_last)

            # format thingspeak request
            request_url = f'https://api.thingspeak.com/channels/{channelID}/feeds.json?start={start_date}&end={end_date}'
            res = requests.get(request_url).json()
            return json.dumps(res)

        else:
            raise cherrypy.HTTPError(501, "No operation!")

    def PUT(self, *uri):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        try:
            platform_ID=uri[0]
            room_ID=uri[1]
            command=uri[2]
            try:
                clients_catalog=self.adaptor.retrieveService('clients_catalog')
                clients_result=requests.get(clients_catalog['url']+"/info/"+platform_ID+"/thingspeak").json()
                client=next((item for item in clients_result if item["room"] == room_ID), False)
                channelID=client["channelID"]
                put_key=client["put_key"]
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
