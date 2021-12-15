import json
import time
from datetime import datetime
from etc.generic_service import *

class NewProfile():
    def __init__(self,platform_ID,platform_name,location, rooms,lastUpdate):
        self.platform_ID=platform_ID
        self.platform_name=platform_name
        self.location=location
        self.lastUpdate=lastUpdate
        self.warning=True
        self.room_cnt=0
        self.rooms=rooms
        
    def jsonify(self):
        profile={"platform_ID":self.platform_ID,'platform_name':self.platform_name,'warning':self.warning,'room_cnt':self.room_cnt,'location':self.location,'rooms':self.rooms,'creation_date':self.lastUpdate}
        return profile

class NewRoom():
    def __init__(self,room_ID,room_name,def_content):
        room_info={}
        room_info['room_ID']=room_ID
        room_info['connection_flag']=False
        room_info['preferences']=self.load_def(def_content,room_name)
        room_info['preferences']['room_name']=room_name
        timestamp=time.time()
        room_info['connection_timestamp']=timestamp
        self.room_info=room_info
    
    def load_def(self,json_content,room_name):
        try:
            info=json_content[room_name.lower()]
        except:
            info=json_content["default"].copy()
        return info 
        
    def jsonify(self):
        return self.room_info

class ProfilesCatalog(Generic_Service):
    def __init__(self,conf_filename, db_filename,def_file="data/default_profile.json"):
        Generic_Service.__init__(self,conf_filename,db_filename)
        self.default_profile=json.load(open(def_file,"r"))

    def retrieveProfileInfo(self,platform_ID):
        notFound=1
        for profile in self.db_content['profiles']:
            if profile['platform_ID']==platform_ID:
                notFound=0
                return profile
        if notFound==1:
            return False

    def retrieveProfileParameter(self,platform_ID,parameter):
        profile=self.retrieveProfileInfo(platform_ID)
        try:
            result= profile[parameter]
        except:
            result=False
        return result

    def insertProfile(self,platform_ID,platform_name):
        notExisting=1
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is False:
            location=None
            rooms=[]
            createdProfile=NewProfile(platform_ID,platform_name,location,rooms,timestamp).jsonify()
            self.db_content['profiles'].append(createdProfile)
            self.db_content['last_creation']=timestamp
            return True
        else:
            return False

    def insertRoom(self,platform_ID,room_name):
        profile=self.retrieveProfileInfo(platform_ID)
        roomNotFound=1
        if profile is not False:
            room_cnt=self.retrieveProfileParameter(platform_ID,'room_cnt')+1
            room_ID="room_"+str(room_cnt)
            new_room=NewRoom(room_ID,room_name,self.default_profile)
            for room in profile['rooms']:
                if room['preferences']['room_name']==room_name:
                    roomNotFound=0
                    break
            if roomNotFound==1:
                profile['rooms'].append(new_room.jsonify())
                self.setParameter(platform_ID,'room_cnt',room_cnt)
                return new_room
            else:
                return False
        else:
            return False

    def associateRoom(self,platform_ID,request_timestamp):
        platform=self.retrieveProfileInfo(platform_ID)
        notFound=1
        if platform is not False:
            for room in platform['rooms']:
                if room['connection_flag'] is False and (request_timestamp-room['connection_timestamp'])<300:
                    room['connection_flag']=True
                    notFound=0
                    return room
            if notFound==1:
                return False
        else:
            return False


    def removeProfile(self,platform_ID):
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is not False:
            self.db_content["profiles"].remove(profile)
            return True
        else:
            return False
        
    def removeRoom(self,platform_ID,room_ID):
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is not False:
            room=self.retrieveRoomInfo(profile['rooms'],room_ID)
            if room is not False:
                profile['rooms'].remove(room)
                return True
            else:
                return False
        else:
            return False
        
        
    def setParameter(self, platform_ID, parameter, parameter_value):
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is not False:
            profile[parameter]=parameter_value
            return True
        else:
            return False
        
    def retrieveRoomInfo(self,rooms,room_ID):
        notFound=1
        for room in rooms:
            if room['room_ID']==room_ID:
                notFound=0
                return room
        if notFound==1:
            return False

    def retrieveRoomList(self, rooms):
        output=[]
        for room in rooms:
            output.append(room['room_ID'])
        return output
        
    def setRoomParameter(self,platform_ID,room_ID,body):
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is not False:
            rooms=profile['rooms']
            room=self.retrieveRoomInfo(rooms,room_ID)
            if room is not False:
                for key in body.keys():
                    try:
                        for subkey in body[key]:
                            room['preferences'][key][subkey]=body[key][subkey]
                        return True
                    except:
                        room['preferences'][key]=body[key]
                        return True
            else:
                return False
        else:
            return False
        
    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.db_content,file, indent=4)









