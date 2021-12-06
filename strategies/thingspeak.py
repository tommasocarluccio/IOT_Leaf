import json
import requests
import sys
import time

class Adapter():
    def __init__(self,filename):
        self.filename=filename
        self.conf_content=json.load(open(self.filename,"r"))
        self.serviceCatalogAddress=self.conf_content['service_catalog']
    
    def retrieveService(self,service):
        r=requests.get(self.serviceCatalogAddress+'/'+service).json()
        return r['url']
    
if __name__ == '__main__':
    filename=sys.arv[1]
    adapter=Adapter(filename)
    while True:
        resourse_catalog=adapter.retrieveService(adapter.conf_content['resource catalog'])
        clients_catalog=adapter.retrieveService(adapter.conf_content['clients catalog'])
        requests.
        
        time.sleep(30)
        
        
        