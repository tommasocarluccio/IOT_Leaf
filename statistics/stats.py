import requests
import json
import numpy as np
import random
import sys
import cherrypy
from datetime import datetime
from dateutil.relativedelta import relativedelta 
from etc.generic_service import *

class ParamDict():
    def __init__(self, name, field):
        self.field=field
        self.name=name
        self.values=[]
    def jsonify(self):
        return ({"name":self.name,"field":self.field,"values":self.values})

class Stats(Generic_Service):
    exposed=True 

    def __init__(self, configuration_file):

        Generic_Service.__init__(self,configuration_file, False)
        self.service = self.registerRequest()
        self.conf_content = json.load(open(configuration_file,"r"))
        self.serviceURL = self.conf_content['service_catalog']


    def calculateStats(self, parameters_list,json_response):
        resp={}
        for param in parameters_list:
            for feed in json_response['feeds']:
                param["values"].append(feed[param["field"]])

            param['values']=np.array(param['values']).astype(float)
            param['values']=param['values'][~(np.isnan(param['values']))]

            resp[param["name"]]={}

            if param['values'].size > 0:
                resp[param['name']]['avg'] = param['values'].mean()
                resp[param['name']]['max'] = param['values'].max()
                resp[param['name']]['min'] = param['values'].min()
                resp[param['name']]['avg_last'] = 0
                resp[param['name']]['Advice']='not enough data'
            else:
                resp[param]['avg'] = 'no_data'
                resp[param]['max'] = 'no_data'
                resp[param]['min'] = 'no_data'

        return resp

    def compute_last_avg(self,parameters_list,body,n):
        for p in parameters_list:
            body[p['name']]['avg_last'] /= n
                
    def GET(self,*uri):
        try:
            platform_ID=uri[0]
            room_ID=uri[1]
            command=uri[2]
            print(command)
            # get today date
            now = datetime.now()
            # get thingspeak adaptor url
            adaptorURL = requests.get(self.serviceURL+'/database_adaptor').json()['url']
        except:
            raise cherrypy.HTTPError(400,"Check your request and try again!")
        
        if command in ['day','week','month']:
            if command=='day':
                last_period_date = now + relativedelta(days=-1)
                output_command='today'
                N = 3
            elif command=='week':
                last_period_date = now + relativedelta(weeks=-1)
                output_command='this week'
                N = 2
            else:
                last_period_date = now + relativedelta(months=-1)
                output_command='this month'
                N = 1

            last = str(last_period_date).split(' ')
            nnow = str(now).split(' ')
            last_period_date_str = '_'.join(last).split('.')[0]
            now_str = '_'.join(nnow).split('.')[0]

            res = requests.get(f'{adaptorURL}/{platform_ID}/{room_ID}/period/{now_str}/{last_period_date_str}').json()
            clients_catalog=self.retrieveService('clients_catalog')
            clients_result=requests.get(clients_catalog['url']+"/info/"+platform_ID+"/thingspeak").json()
            parameters_list=[]
            for room in clients_result:
                if room['room']==room_ID:
                    break
            for field in room['fields']:
                parameters_list.append(ParamDict(room['fields'].get(field),field).jsonify())
            respDEF = self.calculateStats(parameters_list,res)

            try:
                for d in range(N):
                    now = last_period_date
                    if command=='day':
                        last_period_date = now + relativedelta(days=-1)
                    elif command=='week':
                        last_period_date = now + relativedelta(weeks=-1)
                    else:
                        last_period_date = now + relativedelta(months=-1)

                    last = str(last_period_date).split(' ')
                    nnow = str(now).split(' ')
                    last_period_date_str = '_'.join(last).split('.')[0]
                    now_str = '_'.join(nnow).split('.')[0]

                    res = requests.get(f'{adaptorURL}/{platform_ID}/{room_ID}/period/{now_str}/{last_period_date_str}').json()
                    p_list=[]
                    
                    for field in room['fields']:
                        p_list.append(ParamDict(room['fields'].get(field),field).jsonify())

                    resp = self.calculateStats(p_list,res)
                    for p in parameters_list:
                        respDEF[p['name']]['avg_last'] += resp[p['name']]['avg']
                
                self.compute_last_avg(parameters_list,respDEF,N)    

                # print advice msg
                for p in parameters_list:
                    avg=respDEF[p['name']]['avg']
                    avg_last=round(respDEF[p['name']]['avg_last'],2)
                    element_name=p['name']
                    if avg > avg_last:
                        respDEF[p['name']]['Advice'] = f'The average {element_name} {output_command} is higher than the previous {N} {command}s! (avg: {avg_last})'
                    else:
                        respDEF[p['name']]['Advice'] = f'The average {element_name} {output_command} is lower than the previous {N} {command}s! (avg: {avg_last})'
            except Exception as e:
                print("Can't produce advices")

        else:
            raise cherrypy.HTTPError(501, "No operation!")

        
        return json.dumps(respDEF)


if __name__ == "__main__":

    conf = sys.argv[1]
    conf_content=json.load(open(conf,"r"))
    stats = Stats(conf)
    print(conf)

    if stats.service is not False:
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
            }
        }
        cherrypy.tree.mount(stats, stats.service, conf)
        cherrypy.config.update({'server.socket_host': conf_content['IP_address']})
        cherrypy.config.update({'server.socket_port': conf_content['IP_port']})
        cherrypy.engine.start()
        cherrypy.engine.block()

