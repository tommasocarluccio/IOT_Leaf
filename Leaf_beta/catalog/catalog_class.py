import json
from datetime import datetime
import time
from room_catalog import RoomCatalog
#from room import *

class RoomObj():
    def __init__(self,roomID,roomName,thingSpeakURL,devices,timestamp):
        self.roomID=roomID
        self.roomName=roomName
        self.thingSpeakURL=thingSpeakURL
        self.timestamp=timestamp
        self.devices=devices
        
    def jsonify(self):
        room={'roomID':self.roomID,'room_name':self.roomName,'thingSpeakURL':self.thingSpeakURL,'devices':self.devices,'last_update':self.timestamp}
        return room

class RoomsList():
    def __init__(self,filename):
        self.fileContent=json.load(open(filename))
        self.roomsList=[]
        for room in self.fileContent['rooms']:
            self.roomsList.append(RoomObj(room.get('roomID'),room.get('room_name'),room.get('thingSpeakURL'),room.get('devices'),room.get('last_update')).jsonify())
    def show(self):
        print(json.dumps(self.roomsList,indent=4))
        
class Catalog(RoomCatalog):

    def retrieveClientID(self):
        clientID=json.dumps(self.myCatalog["clientID"],indent=4)
        return clientID
        
    def retrieveBroker(self):
        broker=json.dumps(self.myCatalog["broker"],indent=4)
        return broker
    #EX1.3 
    def retrieveAllRooms(self):
        devices=json.dumps(self.myCatalog["rooms"],indent=4)
        return devices
        
    def retrieveRoomsList(self):
        roomsList=[]
        for room in self.myCatalog['rooms']:
            roomsList.append(room['roomID'])
        return json.dumps(roomsList,indent=4)
    
    def retrieveRoomID(self, roomID):
        notFound=1
        for room in self.myCatalog['rooms']:
            if str(room['roomID']) ==(roomID):
                notFound=0
                return json.dumps(room,indent=4)
        if notFound==1:
                    return False

    def changeRoomName(self,roomID,newRoomName):
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        notFound=1
        for room in self.myCatalog['rooms']:
            if str(room['roomID']) ==(roomID):
                notFound=0
                oldRoomName=room['room_name']
                room['room_name']=newRoomName
                self.dateRoomUpload(roomID,timestamp)
                self.save(self.catalogFileName)
                result="'{}' changed to '{}'".format(oldRoomName,newRoomName)
        if notFound==1:
                result="Room not found"
        return result

    def changeClientID(self,newClientID):
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        clientID=self.myCatalog['clientID']
        self.myCatalog['clientID']=newClientID
        self.dateUpload(timestamp)
        self.save(self.catalogFileName)
        result="'{}' changed to '{}'".format(clientID,newClientID) 
        return result
  
    def insertRoom(self,roomID,roomName,thingSpeakURL):
        notExisting=1
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        
        for room in self.myCatalog['rooms']:
            if room['roomID'] == roomID:
                notExisting=0
                
        if notExisting!=0:
            devices=[]
            newRoom=RoomObj(roomID,roomName,thingSpeakURL,devices,timestamp).jsonify()
            self.myCatalog['rooms'].append(newRoom)
            #print(newRoom)
            self.dateUpload(timestamp)
            self.save(self.catalogFileName)
            return True
        else:
            return False
        
    def dateUpload(self,dt_string):
        self.myCatalog['last_update']=dt_string
        
    def removeRoom(self,roomID):
        #myList=[item for item in self.data[roomID].get('devices') if item['sensorID']!=deviceID]
        for room in self.myCatalog['rooms']:
            if room['roomID']==roomID:
                self.myCatalog['rooms'].remove(room)
                self.save(self.catalogFileName)
                return True

   
