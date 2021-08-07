import cherrypy
import json
from datetime import datetime
import sys
import time

# LAB5 EX1
class botRest(object):
    exposed=True
    
    def __init__(self):
        self.test="ciao"
        #self.jsonFile = open(self.catalogFileName, "r") # Open the JSON file for reading 
        #myCatalog = json.load(self.jsonFile) # Read the JSON into the buffer
        #self.jsonFile.close() # Close the JSON file
       
            
    def GET(self,*uri,**params):
        return self.test
        
            
    def PUT (self, *uri, ** params):
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))

        command= str(uri[0])
        if command=='insertCatalog':
            catalogID=json_body['catalogID']
            catalogIP=json_body['addressIP']
            result={"catalogID":catalogID,"catalogIP":catalogIP}
            print(json.dumps(result, indent=4))
            catID_IP.append(result)
            with open('ID_IP.json', 'w') as outfile:
                json.dump(catID_IP, outfile)
        else:
            raise cherrypy.HTTPError(501, "No operation!")

            
if __name__ == '__main__':
    addressIP=sys.argv[1]
    port=int(sys.argv[2])
    
    catID_IP=json.load(open('ID_IP.json'))
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(botRest(), '/bot', conf)
    cherrypy.config.update({'server.socket_host': addressIP})
    cherrypy.config.update({'server.socket_port': port})
    cherrypy.engine.start()
    while True:
            #catalog.c.removeInactive(catalog.inactiveTime)
            time.sleep(2)
    cherrypy.engine.block()


