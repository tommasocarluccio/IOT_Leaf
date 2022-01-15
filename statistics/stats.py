import requests
import json
import numpy as np
import random
import sys
import cherrypy
from datetime import datetime
from dateutil.relativedelta import relativedelta 
from etc.generic_service import *

class Stats(Generic_Service):
    exposed=True 

    def __init__(self, configuration_file):

        Generic_Service.__init__(self,configuration_file, False)
        self.service = self.registerRequest()
        self.conf_content = json.load(open(configuration_file,"r"))
        self.serviceURL = self.conf_content['service_catalog']

    def calculateStats(self, json_response):
        
        AQI = {
            "values": [],
            "field":"field1",
            "name":"AQI"
        }
        temp = {
            "values": [],
            "field":"field3",
            "name":"temp"
        }
        hum = {
            "values": [],
            "field":"field5",
            "name":"hum"
        }
        resp={}
        for param in [AQI, temp, hum]:
            for feed in json_response['feeds']:
                param["values"].append(feed[param["field"]])

            param['values']=np.array(param['values']).astype(float)
            param['values']=param['values'][~(np.isnan(param['values']))]

            resp[param["name"]]={}

            if param['values'].size > 0:
                resp[param['name']]['avg'] = param['values'].mean()
                resp[param['name']]['max'] = param['values'].max()
                resp[param['name']]['min'] = param['values'].min()
            else:
                resp[param]['avg'] = 'no_data'
                resp[param]['max'] = 'no_data'
                resp[param]['min'] = 'no_data'

        return resp
                
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
        
        if command=="day":
            last_period_date = now + relativedelta(days=-1)
            last = str(last_period_date).split(' ')
            nnow = str(now).split(' ')
            last_period_date = '_'.join(last).split('.')[0]
            now = '_'.join(nnow).split('.')[0]

            res = requests.get(f'{adaptorURL}/{platform_ID}/{room_ID}/period/{now}/{last_period_date}').json()        
            respDEF = self.calculateStats(res)

            NUM_DAYS = 1
            avg_lastAQI = 0
            avg_lastTemp = 0
            avg_lastHum = 0

            try:
                # query for avgs of last 7 days
                for d in range(NUM_DAYS):
                    now = last_period_date
                    last_period_date = now + str(relativedelta(days=-1))

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
                avg_lastAQI /= NUM_DAYS
                avg_lastTemp /= NUM_DAYS
                avg_lastHum /= NUM_DAYS

                # print advice msg
                if respDEF['AQI']['avg'] > avg_lastAQI:
                    AQI_avice = f'The average AQI today is higher than the previous {NUM_DAYS} days! (avg: {avg_lastAQI})'
                else:
                    AQI_avice = f'The average AQI today is lower than the previous {NUM_DAYS} days! (avg: {avg_lastAQI})'
                if respDEF['temp']['avg'] > avg_lastTemp:
                    temp_avice = f'The average temperature today is higher than the previous {NUM_DAYS} days! (avg: {avg_lastTemp})'
                else:
                    temp_avice = f'The average temperature today is lower than the previous {NUM_DAYS} days! (avg: {avg_lastTemp})'
                if respDEF['hum']['avg'] > avg_lastHum:
                    hum_avice = f'The average humidity today is higher than the previous {NUM_DAYS} days! (avg: {avg_lastHum})'
                else:
                    hum_avice = f'The average humidity today is lower than the previous {NUM_DAYS} days! (avg: {avg_lastHum})'
            except Exception as e:
                print(e) 
                AQI_avice = 'not enough data'
                temp_avice = 'not enough data'
                hum_avice = 'not enough data'

        elif command=="week":

            last_period_date = now + relativedelta(weeks=-1)
            last = str(last_period_date).split(' ')
            nnow = str(now).split(' ')
            last_period_date = '_'.join(last).split('.')[0]
            now = '_'.join(nnow).split('.')[0]
            
            res = requests.get(f'{adaptorURL}/{platform_ID}/{room_ID}/period/{now}/{last_period_date}').json()
            respDEF = self.calculateStats(res)

            NUM_WEEKS = 4
            avg_lastAQI = 0
            avg_lastTemp = 0
            avg_lastHum = 0

            try: 
                for d in range(NUM_WEEKS):
                    now = last_period_date
                    last_period_date = now + relativedelta(weeks=-1)
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
                avg_lastAQI /= NUM_WEEKS
                avg_lastTemp /= NUM_WEEKS
                avg_lastHum /= NUM_WEEKS

                if respDEF['AQI']['avg'] > avg_lastAQI:
                    AQI_avice = f'The average AQI this week is higher than the previous {NUM_WEEKS} weeks! (avg: {avg_lastAQI})'
                else:
                    AQI_avice = f'The average AQI this week is lower than the previous {NUM_WEEKS} weeks! (avg: {avg_lastAQI})'
                if respDEF['temp']['avg'] > avg_lastTemp:
                    temp_avice = f'The average temperature this week is higher than the previous {NUM_WEEKS} weeks! (avg: {avg_lastTemp})'
                else:
                    temp_avice = f'The average temperature this week is lower than the previous {NUM_WEEKS} weeks! (avg: {avg_lastTemp})'
                if respDEF['hum']['avg'] > avg_lastHum:
                    hum_avice = f'The average humidity this week is higher than the previous {NUM_WEEKS} weeks! (avg: {avg_lastHum})'
                else:
                    hum_avice = f'The average humidity this week is lower than the previous {NUM_WEEKS} weeks! (avg: {avg_lastHum})'
            except:
                'Could not find enough data'
                AQI_avice = 'not enough data'
                temp_avice = 'not enough data'
                hum_avice = 'not enough data'

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
        else:
            raise cherrypy.HTTPError(501, "No operation!")

        respDEF['AQI']['Advice'] = AQI_avice
        respDEF['temp']['Advice'] = temp_avice
        respDEF['hum']['Advice'] = hum_avice

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

