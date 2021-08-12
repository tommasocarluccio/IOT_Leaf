import cherrypy
import json
import requests
import time
import sys

class Service():
    def __init__(self,service_name,ip_address,ip_port):
        self.service_name=service_name
        self.ip_address=ip_address
        self.ip_port=ip_port
    def jsonify(self):
        service={'IP_address':self.ip_address,'port':self.ip_port,'service':"/Leaf/"+self.service_name}
        return service
        
    
class ServiceCatalogREST():
    exposed=True

    def __init__(self,db_filename):
        #configure the service catalog according to information stored inside database
        self.db_filename=db_filename
        self.MyServiceCatalog=json.load(open(self.db_filename,"r"))
        self.serviceCatalogIP=self.MyServiceCatalog['service_catalog'][0].get('IP_address')
        self.serviceCatalogPort=self.MyServiceCatalog['service_catalog'][0].get('port')
        self.service=self.MyServiceCatalog['service_catalog'][0].get('service')
        
        
    def retrieveInfo(self,catalog,service):
        serviceAddress='http://'+catalog[service][0].get("IP_address")+':'+str(catalog[service][0].get("port"))
        return serviceAddress
    
    def findService(self,name):
        #search if a given service is registered
        if name in self.MyServiceCatalog:
            return True
        else:
            return False
        
    def registry(self,name,IP,port):
        try:
            new_service=Service(name,IP,port)
            if self.findService(name):
                self.removeService(new_service.service_name)
            
            self.MyServiceCatalog[name]=[]    
            self.MyServiceCatalog[name].append(new_service.jsonify())
            return True
        except:
            return False
    
    def removeService(self,service):
        del self.MyServiceCatalog[service]
        
    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.MyServiceCatalog,file, indent=4)


    def GET(self,*uri):
        if len(uri)!=0:
            try:
                output=self.MyServiceCatalog[str(uri[0])][0]
            except:
                raise cherrypy.HTTPError(404,"Service: Not found")
        else:
            output=self.MyServiceCatalog['description'] #if no resource is found, it return a general description about database

        return json.dumps(output,indent=4) 

    def POST(self,*uri):
        successFlag=0
        if len(uri)!=0:
            if uri[0]=="register":
                try:
                    body=cherrypy.request.body.read()
                    json_body=json.loads(body.decode('utf-8'))
                    new_service=self.registry(json_body['service'],json_body['IP_address'],json_body['port'])
                    if new_service is not False:
                        output="Service '{}' updated".format(json_body['service'])
                        successFlag=1
                    else:
                        output="Service '{}'- Registration failed".format(json_body['service'])
                except IndexError as e:
                    print(e)
                    output="Error request."
            else:
                raise cherrypy.HTTPError(501, "No operation!")
        print(output)
        if successFlag==1:
            self.save()
            return json.dumps(new_service,indent=4)
        
    def DELETE(self,*uri):
        if len(uri)!=0:
            if uri[0]=="delete":
                try:
                    self.removeService(uri[1])
                    print("Service '{}' deleted".format(uri[1]))
                    self.save()
                except IndexError as e:
                    print(e)
                    print("Error request.")
            else:
                raise cherrypy.HTTPError(501, "No operation!")
        
                
        
        


if __name__ == '__main__':
    settings=sys.argv[1]
    serviceCatalog=ServiceCatalogREST(settings)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(serviceCatalog, serviceCatalog.service, conf)
    cherrypy.config.update({'server.socket_host': serviceCatalog.serviceCatalogIP})
    cherrypy.config.update({'server.socket_port': serviceCatalog.serviceCatalogPort})
    cherrypy.engine.start()
    while True:
        time.sleep(1)
    cherrypy.engine.block()
