import json
from datetime import datetime
import time

#it could be useless if a specific structure is not imposed.
class RoomObj():
    def __init__(self,room_ID,MRT,devices,timestamp):
        self.room_ID=room_ID
        self.MRT=MRT
        self.timestamp=timestamp
        self.devices=devices
        
    def jsonify(self):
        room={'room_ID':self.room_ID,'devices':self.devices,'last_update':self.timestamp}
        return room

        
class RoomsCatalog():
    def __init__(self,myRooms):
        self.myRooms=myRooms
        self.now=datetime.now()
        self.timestamp=self.now.strftime("%d/%m/%Y %H:%M")

    def findPos(self,room_ID):
        notFound=1
        for i in range(len(self.myRooms)): 
            if self.myRooms[i]['room_ID']==room_ID:
                notFound=0
                return i
        if notFound==1:
            return False

    def setParameter(self, room_ID, parameter, parameter_value):
        if parameter != "room_ID":
            i=self.findPos(room_ID)
            if i is not False:
                self.myRooms[i][parameter]=parameter_value
                return True
            else:
                return False
        else:
            return False

    def insertRoom(self,room_ID,room):
        i=self.findPos(room_ID)
        output=True
        if i is not False:
            self.removeRoom(room_ID)
            output=False

        self.myRooms.append(room)
        return output

    def removeRoom(self,room_ID):
        i=self.findPos(room_ID)
        if i is not False:
            self.myRooms.pop(i) 
            return True
        else:
            return i


   

