from catalog_class import * 
import cherrypy
import json
from datetime import datetime
import sys

# LAB5 EX1
class CatalogManager(object):
    exposed=True
    
    def __init__(self,catalogFileName):
            self.catalogFileName=catalogFileName
            self.jsonFile = open(self.catalogFileName, "r") # Open the JSON file for reading 
            myCatalog = json.load(self.jsonFile) # Read the JSON into the buffer
            self.jsonFile.close() # Close the JSON file
            self.c= Catalog(myCatalog,self.catalogFileName)
            
    def GET(self,*uri,**params):
        result=False

        if len(uri)!=0:
            resource= str(uri[0])

            if resource=='clientID':
                #GET 0.0.0.0:8080/clientID
                result=self.c.retrieveClientID()
                #print(result)
            elif resource=='broker':
                #GET 0.0.0.0:8080/broker
                result=self.c.retrieveBroker()
            elif resource=='roomsList':
                result=self.c.retrieveRoomsList()
            elif resource=='rooms':
                try:
                    roomID=str(uri[1])
                    try:
                        if str(uri[2])=="devices":
                            try:
                                deviceID=str(uri[3])
                                try:
                                    parameter=str(params['parameter'])
                                    result=self.c.retrieveValue(roomID,deviceID,parameter)
                                except:
                                    result=self.c.retrieveDeviceID(roomID,deviceID)
                                
                            except:
                                result=self.c.retrieveAllDevices(roomID)
                                
                        else:
                            pass
                    
                    except:
                        result=self.c.retrieveRoomID(roomID)

                except:
                    result=self.c.retrieveAllRooms()
                    #print(result)

            else:
                raise cherrypy.HTTPError(501, "No operation!")
            if result==False:
                raise cherrypy.HTTPError(404,"Not found")
            else:
                return result 
            
    def PUT (self, *uri, ** params):
        # UNDERSTAND REQUEST BODY
        body=cherrypy.request.body.read()
        json_body=json.loads(body.decode('utf-8'))
        #print(json_body)
        command= str(uri[0])
        if command=='insertDevice':
            roomID=str(params['room'])
            newCatalog=self.c.insertDevice(roomID,json_body['sensorID'], json_body['end_points'], json_body['parameters'])    
            result="Device {} has been added to Catalogue".format(json_body['sensorID'])
            

        if command=='insertRoom':
            roomID=json_body['roomID']
            newCatalog=self.c.insertRoom(roomID)
            if newCatalog==True:
                result="Room '{}'' has been added to Catalogue".format(roomID)
            else:
                result="'{}'' already exists!".format(roomID)
            return result

        if command=='changeRoomName':
            roomID=json_body['roomID']
            newRoomName=json_body['newRoomName']
            output=self.c.changeRoomName(roomID,newRoomName)
            print(output)

        if command=='changeClientID':
            newClientID=json_body['newClientID']
            output=self.c.changeClientID(newClientID)
            print(output)


    def DELETE(self, *uri, ** params):
        if str(uri[0])== 'removeDevice':
            roomID=str(params['room'])
            deviceID=str(params['device'])
            result=self.c.removeDevice(roomID,deviceID)
            if result==True:
                output=f"Device with ID {deviceID} has been removed" 
                print (output)
            else:
                raise cherrypy.HTTPError(404,"Not found")
        elif str(uri[0])=='removeRoom':
            roomID=str(params['room'])
            result=self.c.removeRoom(roomID)
            if result==True:
                output=f"Room with ID {roomID} has been removed" 
                print (output)
            else:
                raise cherrypy.HTTPError(404,"Not found")
            
                
        else:
            raise cherrypy.HTTPError(501, "No operation!")


if __name__ == '__main__':
    settings=sys.argv[1]
    catalog=CatalogManager(settings)
    catalog.c.pingBot('http://127.0.0.1:8081')
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(catalog, '/catalog', conf)
    cherrypy.config.update({'server.socket_host': catalog.c.addressIP })
    cherrypy.config.update({'server.socket_port': catalog.c.port})
    cherrypy.engine.start()
    while True:
            #catalog.c.removeInactive(catalog.c.inactiveTime)
        time.sleep(2)
    cherrypy.engine.block()


