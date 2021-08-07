import json
from datetime import datetime

class RoomObj():
    def __init__(self,roomID,roomName,devices,timestamp):
        self.roomID=roomID
        self.roomName=roomName
        self.timestamp=timestamp
        self.devices=devices
    
    def jsonify(self):
        room={'roomID':self.roomID,'room_name':self.roomName,'devices':self.devices,'timestamp':self.timestamp}
        return room

class RoomsList():
    def __init__(self,filename):
        self.fileContent=json.load(open(filename))
        self.roomsList=[]
        for room in self.fileContent['rooms']:
            self.roomsList.append(RoomObj(room.get('roomID'),room.get('room_name'),room.get('devices'),room.get('last_update')).jsonify())
    def show(self):
        print(json.dumps(self.roomsList,indent=4))
    