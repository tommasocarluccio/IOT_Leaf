import json
import time
from datetime import datetime
from generic_service import *

class NewProfile():
    def __init__(self,platform_ID,platform_name,inactiveTime, location, rooms,lastUpdate):
        self.platform_ID=platform_ID
        self.platform_name=platform_name
        self.inactiveTime=inactiveTime
        self.location=location
        self.lastUpdate=lastUpdate
        self.warning=False
        self.room_cnt=0
        self.rooms=rooms
        
    def jsonify(self):
        profile={"platform_ID":self.platform_ID,'platform_name':self.platform_name,'warning':self.warning,'room_cnt':self.room_cnt,'inactive_time':self.inactiveTime,'location':self.location,'rooms':self.rooms,'last_update':self.lastUpdate}
        return profile

class NewRoom():
    def __init__(self,room_ID,room_info,def_content):
        room_info['room_ID']=room_ID
        room_info['connection_flag']=False
        room_info['preferences']=self.load_def(def_content,room_info['room_name'])
        timestamp=time.time()
        room_info['connection_timestamp']=timestamp
        self.room_info=room_info
    
    def load_def(self,json_content,room_name):
        try:
            info=json_content[room_name.lower()]
        except:
            info=json_content["default"]
        return info 
        
    def jsonify(self):
        return self.room_info

class ProfilesCatalog(Generic_Service):
    def __init__(self,conf_filename, db_filename,def_file="etc/default_profile.json"):
        Generic_Service.__init__(self,conf_filename,db_filename)
        self.default_profile=json.load(open(def_file,"r"))
        #self.delta=self.profilesContent['delta']
        #self.profilesListCreate()

    def retrieveProfileInfo(self,platform_ID):
        notFound=1
        for profile in self.db_content['profiles']:
            if profile['platform_ID']==platform_ID:
                notFound=0
                return profile
        if notFound==1:
            return False
    """    
    def buildWeatherURL(self,city):
        basic_url=self.profilesContent["weather_api"]
        api_key=self.profilesContent['weather_key']
        url=basic_url+"?q="+city+"&appid="+api_key+"&units=metric"
        return url
    """
    """
    def createBody(self,platform_ID,city,input_body):
        lat=input_body['coord'].get('lat')
        long=input_body['coord'].get('lon')
        condition=input_body['weather'][0].get('main')
        temp=float(input_body['main'].get('temp'))
        temp_feel=float(input_body['main'].get('feels_like'))
        hum=int(input_body['main'].get('humidity'))
        wind_speed=float(input_body['wind'].get('speed'))
        wind_deg=int(input_body['wind'].get('deg'))
        
        final_dict={"lat":lat,"lon":long,"condition":condition,"temp_ext":temp,"temp_ext_feel":temp_feel,"hum_ext":hum,"wind_speed":wind_speed,"wind_deg":wind_deg,"city":city}
        
        rfc=datetime.fromtimestamp(time.time())
        rfc=rfc.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        json_body = [{"measurement":"external","tags":{"user":platform_ID},"time":rfc,"fields":final_dict}]
        return json_body
    """

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
            inactiveTime=3600
            rooms=[]
            createdProfile=NewProfile(platform_ID,platform_name,inactiveTime,location,rooms,timestamp).jsonify()
            self.db_content['profiles'].append(createdProfile)
            return True
        else:
            return False

    def insertRoom(self,platform_ID,room_info):
        profile=self.retrieveProfileInfo(platform_ID)
        roomNotFound=1
        if profile is not False:
            room_cnt=self.retrieveProfileParameter(platform_ID,'room_cnt')+1
            room_ID="room_"+str(room_cnt)
            new_room=NewRoom(room_ID,room_info,self.default_profile)
            for room in profile['rooms']:
                if room['room_name']==room_info['room_name']:
                    roomNotFound=0
                    break
            if roomNotFound==1:
                profile['rooms'].append(new_room.jsonify())
                self.setParameter(platform_ID,'room_cnt',room_cnt)
                return True
            else:
                return False
        else:
            return False

    def associateRoom(self,platform_ID,request_timestamp):
        pos=self.findPos(platform_ID)
        notFound=1
        if pos is not False:
            for pref in self.profilesContent['profiles'][pos]['preferences']:
                if pref['connection_flag'] is False and (request_timestamp-pref['connection_timestamp'])<300:
                    pref['connection_flag']=True
                    notFound=0
                    return True,pref
            if notFound==1:
                return False,False
        else:
            return False,False


    def removeProfile(self,platform_ID):
        profile=self.retrieveProfileInfo(platform_ID)
        print(profile)
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
        
    def setRoomParameter(self,platform_ID,room_ID,parameter,parameter_value):
        profile=self.retrieveProfileInfo(platform_ID)
        if profile is not False:
            rooms=profile['rooms']
            room=self.retrieveRoomInfo(rooms,room_ID)
            if room is not False:
                room[parameter]=parameter_value
                return True
            else:
                return False
    """      
    def createDevicesList(self,platform_ID,room_ID,devices_list):
        pos=self.findPos(platform_ID)
        if pos is not False:
            rooms=self.profilesContent['profiles'][pos]["preferences"]
            room=self.retrieveRoomInfo(rooms,room_ID)
            room["devices"]=[]
            if room is not False:
                for device in devices_list:
                    device_new={}
                    device_new["device_ID"]=device["device_ID"]
                    device_new["last_update"]=(device["timestamp"])
                    device_new["parameters"]=[]
                    for parameter in device['parameters']:
                        parameter_new={}
                        parameter_new["parameter"]=(parameter['parameter'])
                        parameter_new["unit"]=(parameter['unit'])
                        device_new["parameters"].append(parameter_new)
                    room["devices"].append(device_new)
                
                return True
            else:
                return False
    """
        
    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.db_content,file, indent=4)









