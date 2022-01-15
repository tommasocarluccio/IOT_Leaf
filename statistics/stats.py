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
                N = 1
            elif command=='week'::
                last_period_date = now + relativedelta(weeks=-1)
                N = 1
            else:
                last_period_date = now + relativedelta(months=-1)
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

            # query for avgs of last 7 days
            try:
                for d in range(NUM_DAYS):
                    now = last_period_date
                    last_period_date = now + relativedelta(days=-1)

                    last = str(last_period_date).split(' ')
                    nnow = str(now).split(' ')
                    last_period_date = '_'.join(last).split('.')[0]
                    now = '_'.join(nnow).split('.')[0]

                    res = requests.get(f'{adaptorURL}/{platform_ID}/{room_ID}/period/{now}/{last_period_date}').json()
                    p_list=[]
                    
                    for field in room['fields']:
                        p_list.append(ParamDict(room['fields'].get(field),field).jsonify())

                    resp = self.calculateStats(p_list,res)
                    for p in parameters_list:
                        respDEF[p['name']]['avg_last']+= resp[p['name']]['avg']
                
                self.compute_last_avg(parameters_list,respDEF,N)    

                # print advice msg
                for p in parameters_list:
                    avg=respDEF[p['name']]['avg']
                    avg_last=respDEF[p['name']]['avg_last']
                    element_name=p['name']

                    if avg > avg_last:
                        respDEF[p['name']]['Advice'] = f'The average {element_name} this week is higher than the previous {NUM_DAYS} {command}s! (avg: {round(avg_last,2)})'
                    else:
                        respDEF[p['name']]['Advice'] = f'The average {element_name} today is lower than the previous {NUM_DAYS} {command}s! (avg: {round(avg_last,2)}'
            except Exception as e:
                print(e)


       """

        elif command=="month":
            last_period_date = now + relativedelta(months=-1)
            last = str(last_period_date).split(' ')
            nnow = str(now).split(' ')
            last_period_date = '_'.join(last).split('.')[0]
            now = '_'.join(nnow).split('.')[0]
            res = requests.get(f'{adaptorURL}/{platform_ID}/{room_ID}/period/{now}/{last_period_date}').json()
            respDEF = self.calculateStats(res)

            NUM_MONTHS = 2
            avg_lastAQI = 0
            avg_lastTemp = 0
            avg_lastHum = 0

            try:
                for d in range(NUM_MONTHS):
                    now = last_period_date
                    last_period_date = now + relativedelta(months=-1)
                    last = str(last_period_date).split(' ')
                    nnow = str(now).split(' ')
                    last_period_date = '_'.join(last).split('.')[0]
                    now = '_'.join(nnow).split('.')[0]
                    print(last_period_date)
                    
                    res = requests.get(f'{adaptorURL}/{platform_ID}/{room_ID}/period/{now}/{last_period_date}').json()

                    resp = self.calculateStats(res)
                    avg_lastAQI += resp['AQI']['avg']
                    avg_lastTemp += resp['temp']['avg']
                    avg_lastHum += resp['hum']['avg']
                avg_lastAQI /= NUM_MONTHS
                avg_lastTemp /= NUM_MONTHS
                avg_lastHum /= NUM_MONTHS

                if respDEF['AQI']['avg'] > avg_lastAQI:
                    AQI_avice = f'The average AQI this month is higher than the previous {NUM_MONTHS} months! (avg: {avg_lastAQI})'
                else:
                    AQI_avice = f'The average AQI this month is lower than the previous {NUM_MONTHS} months! (avg: {avg_lastAQI})'
                if respDEF['temp']['avg'] > avg_lastTemp:
                    temp_avice = f'The average temperature this month is higher than the previous {NUM_MONTHS} months! (avg: {avg_lastTemp})'
                else:
                    temp_avice = f'The average temperature this month is lower than the previous {NUM_MONTHS} months! (avg: {avg_lastTemp})'
                if respDEF['hum']['avg'] > avg_lastHum:
                    hum_avice = f'The average humidity this month is higher than the previous {NUM_MONTHS} months! (avg: {avg_lastHum})'
                else:
                    hum_avice = f'The average humidity this month is lower than the previous {NUM_MONTHS} months! (avg: {avg_lastHum})'
            except:
                'Could not find enough data'
                AQI_avice = 'not enough data'
                temp_avice = 'not enough data'
                hum_avice = 'not enough data'
        """
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

