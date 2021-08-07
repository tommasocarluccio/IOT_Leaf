from catalog_class import * 
import cherrypy
import json
from datetime import datetime
import sys

class CatalogManager(object):
    exposed=True
    
    def __init__(self,catalogFileName):
            self.catalogFileName=catalogFileName
            self.jsonFile = open(self.catalogFileName, "r") # Open the JSON file for reading 
            self.myCatalog = json.load(self.jsonFile) # Read the JSON into the buffer
            #self.jsonFile.close() # Close the JSON file
            self.addressIP=self.myCatalog['catalog'][0].get('addressIP')
            self.port=self.myCatalog['catalog'][0].get('port')
            self.inactiveTime=self.myCatalog['inactiveTime']
            self.c= Catalog(self.myCatalog,self.catalogFileName)
            print("\n%% Running Catalogue %%\n")
    def GET(self,*uri,**params):
        result=False

        if len(uri)!=0:
            resource= str(uri[0])

            if resource=='clientID':
                result=self.c.retrieveClientID()
            elif resource=='broker':
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
            if newCatalog==True:
                output="Device {} in {} has been added to Catalogue".format(json_body['sensorID'],roomID)
            else:
                output="Catalog updated: {}-{}".format(json_body['sensorID'],roomID)
            
        if command=='insertRoom':
            roomID=json_body['roomID']
            roomName=json_body['roomName']
            thingSpeakURL=json_body['thingSpeakURL']
            newCatalog=self.c.insertRoom(roomID,roomName,thingSpeakURL)
            if newCatalog==True:
                output="Room '{}' has been added to Catalogue".format(roomID)
            else:
                output="'{}' already exists!".format(roomID)

        if command=='changeRoomName':
            roomID=json_body['roomID']
            newRoomName=json_body['newRoomName']
            output=self.c.changeRoomName(roomID,newRoomName)

        if command=='changeClientID':
            newClientID=json_body['newClientID']
            output=self.c.changeClientID(newClientID)
        
        if command=='insertValue':
            roomID=json_body['roomID']
            output=self.c.insertValue(roomID,json_body['sensorID'],json_body['parameter'],json_body['value'])
        
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
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }
    cherrypy.tree.mount(catalog, '/catalog', conf)
    cherrypy.config.update({'server.socket_host': catalog.addressIP })
    cherrypy.config.update({'server.socket_port': catalog.port})
    cherrypy.engine.start()
    while True:
            for room in catalog.myCatalog['rooms']:
                catalog.c.removeInactive(room['roomID'],catalog.inactiveTime)
            time.sleep(2)
    cherrypy.engine.block()


