import json

class Service():
    def __init__(self,service_name,ip_address,ip_port):
        self.service_name=service_name
        self.ip_address=ip_address
        self.ip_port=ip_port
        self.url=self.create_url()
    
    def create_url(self):
        url="http://"+self.ip_address+":"+str(self.ip_port)+"/"+self.service_name
        return url
    
    def jsonify(self):
        service={'IP_address':self.ip_address,'port':self.ip_port,'service':'/'+self.service_name,'url':self.url}
        return service

class ServiceCatalog(object):
    def __init__(self,db_filename):
        #configure the service catalog according to information stored inside database
        self.db_filename=db_filename
        self.content=json.load(open(self.db_filename,"r"))
        self.serviceCatalogIP=self.content['service_catalog'].get('IP_address')
        self.serviceCatalogPort=self.content['service_catalog'].get('port')
        self.service=self.content['service_catalog'].get('service')

                
    def retrieveInfo(self,catalog,service):
        serviceAddress='http://'+catalog[service].get("IP_address")+':'+str(catalog[service].get("port"))
        return serviceAddress
    
    def findService(self,name):
        #search if a given service is registered
        if name in self.content:
            return True
        else:
            return False
        
    def registry(self,name,IP,port):
        try:
            new_service=Service(name,IP,port)
            if self.findService(name):
                self.removeService(new_service.service_name)
            
            self.content[name]=new_service.jsonify()
            return new_service.jsonify()['service']
        except Exception as e:
            
            return False
    
    def removeService(self,service):
        if self.findService(service):
            del self.content[service]
            return True
        
        else:
            return False
    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.content,file, indent=4)