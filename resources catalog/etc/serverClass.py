import json
from datetime import datetime
import time
from etc.rooms_catalog import RoomsCatalog
from etc.devices_catalog import DevicesCatalog
from etc.generic_service import *

class NewPlatform():
    def __init__(self,platform_ID,rooms,last_update):
        self.platform_ID=platform_ID
        self.rooms=rooms
        self.lastUpdate=last_update
        
    def jsonify(self):
        platform={'platform_ID':self.platform_ID,'rooms':self.rooms,'creation_date':self.lastUpdate}
        return platform
    
class ResourceService(Generic_Service):
    def __init__(self,conf_filename,db_filename):
        Generic_Service.__init__(self,conf_filename,db_filename)
        self.delta=self.conf_content.get('delta')
                
    def retrievePlatformsList(self):
        platformsList=[]
        for platform in self.db_content['platforms_list']:
            platformsList.append(platform['platform_ID'])
        return platformsList
    
    def retrievePlatform(self,platform_ID):
        notFound=1
        for platform in self.db_content['platforms_list']:
            if platform['platform_ID']==platform_ID:
                notFound=0
                return platform
        if notFound==1:
            return False

    def retrieveRoomInfo(self,platform_ID,room_ID):
        notFound=1
        platform=self.retrievePlatform(platform_ID)
        if platform is not False:
            for room in platform['rooms']:
                if room['room_ID']==room_ID:
                    notFound=0
                    return room
            if notFound==1:
                return False
        else:
            return False

    def retrieveDeviceInfo(self,platform_ID,room_ID,device_ID):
        notFound=1
        room=self.retrieveRoomInfo(platform_ID,room_ID)
        for device in room['devices']:
            if device['deviceID']==device_ID:
                notFound=0
                return device
        if notFound==1:
            return False

    def retrieveParameterInfo(self,platform_ID,room_ID,device_ID,parameter_name):
        notFound=1
        device=self.retrieveDeviceInfo(platform_ID,room_ID,device_ID)
        for parameter in device['resources']:
            if parameter['n']==parameter_name:
                notFound=0
                return parameter
        if notFound==1:
            return False

    def findParameter(self,platform_ID,room_ID,parameter_name):
        notFound=1
        room=self.retrieveRoomInfo(platform_ID,room_ID)
        try:
            p=room[parameter_name]
            parameter={"parameter":parameter_name,"value":p}
            return parameter
        except:
            for device in room['devices']:
                parameter=self.retrieveParameterInfo(platform_ID,room_ID,device['deviceID'],parameter_name)
                if parameter is not False:
                    notFound=0
                    new_parameter=parameter.copy()
                    new_parameter['deviceID']=device['deviceID']
                    return new_parameter
            if notFound==1:
                return False

        
    def insertPlatform(self,platform_ID,rooms):
        notExisting=1
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        platform=self.retrievePlatform(platform_ID)
        if platform is False:
            createdPlatform=NewPlatform(platform_ID,rooms,timestamp).jsonify()
            self.db_content['platforms_list'].append(createdPlatform)
            return True
        else:
            return False

    def insertRoom(self,platform_ID,room_ID,room):
        platform=self.retrievePlatform(platform_ID)
        existingFlag=False
        self.roomsCatalog=RoomsCatalog(platform['rooms'])
        existingFlag=self.roomsCatalog.insertRoom(room_ID,room)
        if existingFlag:
            output="Platform '{}' - Room '{}' has been added to Server".format(platform_ID, room_ID)
        else:
            output="Platform '{}' - Room '{}' already exists. Resetted...".format(platform_ID,room_ID)

    def insertDevice(self,platform_ID,room_ID,msg):
        print(platform_ID+"-->"+room_ID)
        room=self.retrieveRoomInfo(platform_ID,room_ID)
        if room is not False:
            catalog=DevicesCatalog(room['devices'])
            #print(msg)
            device_ID=msg['bn']
            result=catalog.insertValue(device_ID,msg)
            if result is False:
                print("Not saving..")
                return False
            else:
                return True
        else:
            return False
   
    def removePlatform(self,platform_ID):
        notFound=True
        for i in range(len(self.db_content['platforms_list'])):
            if self.db_content['platforms_list'][i]['platform_ID']==platform_ID:
                self.db_content['platforms_list'].pop(i)
                notFound=False
                return True
        if notFound:
            return False

    def removeRoom(self,platform_ID,room_ID):
        platform=self.retrievePlatform(platform_ID)
        if platform is not False:
            roomsCatalog=RoomsCatalog(platform['rooms'])
            result=roomsCatalog.removeRoom(room_ID)
            return result
        else:
            return False

    def removeDevice(self,platform_ID,room_ID,device_ID):
        room=self.retrieveRoomInfo(platform_ID,room_ID)
        if room is not False:
            devicesCatalog=DevicesCatalog(room['devices'])
            result=devicesCatalog.removeDevice(device_ID)
            return result
        else:
            return False

    def removeInactive(self,inactiveTime):
        for platform in self.db_content['platforms_list']:
            for room in platform['rooms']:
                devices=room['devices']
                devicesCatalog=DevicesCatalog(devices)
            return devicesCatalog.removeInactive(inactiveTime)

    def dateUpdate(self,element):
        now=datetime.now()
        new_date=now.strftime("%d/%m/%Y/%H/%M")
        element['last_update']=new_date

    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.db_content,file, indent=4)
