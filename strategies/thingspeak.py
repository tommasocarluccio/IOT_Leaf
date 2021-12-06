import json
import requests
import sys
import time

class Adapter():
    def __init__(self,filename):
        self.filename=filename
        self.conf_content=json.load(open(self.filename,"r"))
        self.serviceCatalogAddress=self.conf_content['service_catalog']
        self.time_sleep=self.conf_content['time_sleep']
        self.last_update=time.time()
        self.thingspeak_url=self.conf_content['thingspeak_url']
    
    def retrieveService(self,service):
        r=requests.get(self.serviceCatalogAddress+'/'+service).json()
        return r['url']
    
    def retrieveParams(self,clients_result,resource_catalog):
        params={"api_key":clients_result["write_key"]}
        room_ID=clients_result['room']
        for field in clients_result['fields']:
            parameter=clients_result['fields'].get(field)
            try:
                resource_result=requests.get("{}/{}/{}?parameter={}".format(resource_catalog,platform,room_ID,parameter)).json()
                if not self.check_time(resource_result['t']):
                    resource_result["v"]=None
                #print(resource_result)
            except:
                resource_result["v"]=None
            params[field]=resource_result["v"]
        return params
            
    
    def check_time(self,timestamp):
        if timestamp>self.last_update:
            return True
        else:
            return False
            
    def send(self,clients,command,params):
        try:
            print("Sending data for {}".format(clients['room']))
            r=requests.post("{}{}".format(self.thingspeak_url,command),params=params)
            self.last_update=time.time()
            print("Success!\n")
        except Exception as e:
            print(e)
    
if __name__ == '__main__':
    filename=sys.argv[1]
    adapter=Adapter(filename)
    while True:
        resource_catalog=adapter.retrieveService(adapter.conf_content['resource catalog'])
        clients_catalog=adapter.retrieveService(adapter.conf_content['clients catalog'])
        platforms_list=requests.get(resource_catalog+"/platformsList").json()
        for platform in platforms_list:
            print(platform)
            clients_result=requests.get(clients_catalog+"/info/"+platform+"/thingspeak").json()
            params=adapter.retrieveParams(clients_result,resource_catalog)
            command="update"
            adapter.send(clients_result,command,params)
            
        time.sleep(adapter.time_sleep)
        
        
        