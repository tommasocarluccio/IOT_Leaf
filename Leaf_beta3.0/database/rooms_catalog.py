import json
from datetime import datetime
import time

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
        
class RoomsCatalog():
    def __init__(self,myRooms):
        self.myRooms=myRooms
        self.now=datetime.now()
        self.timestamp=self.now.strftime("%d/%m/%Y %H:%M")
    
    def retrieveAllRooms(self):
        rooms=self.myRooms
        return rooms
        
    def retrieveRoomsList(self):
        roomsList=[]
        for room in self.myRooms:
            roomsList.append(room['roomID'])
        return roomsList
        
    def retrieveRoomID(self, roomID):
        notFound=1
        for room in self.myRooms:
            if str(room['roomID']) ==(roomID):
                notFound=0
                return room
        if notFound==1:
            return False

    def changeRoomName(self,roomID,newRoomName):
        room=self.retrieveRoomID(roomID)
        if room is not False:
            oldRoomName=room['room_name']
            room['room_name']=newRoomName
            self.dateRoomUpdate(roomID,self.timestamp)
            result="'{}' changed to '{}'".format(oldRoomName,newRoomName)
        else:
            result=False
        return result

    def insertRoom(self,roomID,roomName,devices,thingSpeakURL):
        room=self.retrieveRoomID(roomID)
        if room is False:
            newRoom=RoomObj(roomID,roomName,thingSpeakURL,devices,self.timestamp).jsonify()
            self.myRooms.append(newRoom)
            return True
        else:
            room['room_name']=roomName
            self.dateRoomUpdate(roomID,self.timestamp)
            return False
        
    def dateRoomUpdate(self,roomID,dt_string):
        self.data={x['roomID']: x for x in self.myRooms}
        self.data[roomID]['last_update']=dt_string
        
    def removeRoom(self,roomID):
        room=self.retrieveRoomID(roomID)
        if room is not False:
            self.myRooms.remove(room)
            self.dateRoomUpdate(roomID,self.timestamp)
            return True
        else:
            return False


   

