import json
from datetime import datetime
import time
from rooms_catalog import RoomsCatalog
from devices_catalog import DevicesCatalog
from conf.generic_service import *
from conf.MyMQTT import *

class NewPlatform():
    def __init__(self,platform_ID,rooms,last_update):
        self.platform_ID=platform_ID
        self.rooms=rooms
        #self.local_IP=local_IP
        self.lastUpdate=last_update
        
    def jsonify(self):
        platform={'platform_ID':self.platform_ID,'rooms':self.rooms,'creation_date':self.lastUpdate}
        return platform

class DataCollector():
    def __init__(self,clientID,brokerIP,brokerPort,notifier):
        self.clientID=clientID
        self.brokerIP=brokerIP
        self.brokerPort=brokerPort
        self.notifier=notifier
        self.client=MyMQTT(self.clientID,self.brokerIP,self.brokerPort,self.notifier)
    def run(self):
        self.client.start()
        print('{} has started'.format(self.clientID))
    def end(self):
        self.client.stop()
        print('{} has stopped'.format(self.clientID))
    def follow(self,topic):
        self.client.mySubscribe(topic)
    def unfollow(self,topic):
        self.client.unsubscribe(topic)
        
    
class ResourceService(Generic_Service):
    def __init__(self,conf_filename,db_filename):
        Generic_Service.__init__(self,conf_filename,db_filename)
        
    def notify(self,topic,msg):
        payload=json.loads(msg)
        #print(payload)
        platform_ID=payload['bn'].split("/")[0]
        room_ID=payload['bn'].split("/")[1]
        device_ID=payload['bn'].split("/")[2]
        e=payload['e']
        self.insertValue(platform_ID,room_ID,device_ID,payload)
        
    def insertValue(self,platform_ID,room_ID,device_ID,msg):
        room=self.retrieveRoomInfo(platform_ID,room_ID)
        if room is not False:
            catalog=DevicesCatalog(room['devices'])
            msg['bn']=device_ID
            result=catalog.insertValue(device_ID,msg)
            if result:
                print(platform_ID+": " + device_ID+" updated in " + room_ID)
                self.save()
                
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
        for room in platform['rooms']:
            if room['room_ID']==room_ID:
                notFound=0
                return room
        if notFound==1:
            return False

    def retrieveDeviceInfo(self,platform_ID,room_ID,device_ID):
        notFound=1
        room=self.retrieveRoomInfo(platform_ID,room_ID)
        for device in room['devices']:
            if device['device_ID']==device_ID:
                notFound=0
                return device
        if notFound==1:
            return False

    def retrieveParameterInfo(self,platform_ID,room_ID,device_ID,parameter_name):
        notFound=1
        device=self.retrieveDeviceInfo(platform_ID,room_ID,device_ID)
        for parameter in device['parameters']:
            if parameter['parameter']==parameter_name:
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
                parameter=self.retrieveParameterInfo(platform_ID,room_ID,device['device_ID'],parameter_name)
                if parameter is not False:
                    notFound=0
                    new_parameter=parameter.copy()
                    new_parameter['device_ID']=device['device_ID']
                    return parameter
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
        return existingFlag

    
    def insertDevice(self,room,device_ID,device):
        self.devicesCatalog=DevicesCatalog(room['devices'])
        new_device=self.devicesCatalog.insertDevice(device_ID,device)
        
        return new_device

    def insertDeviceValue(self, platform_ID, room_ID, device_ID, dictionary):
        i=self.findPos(platform_ID)
        if i is not False:
            self.roomsCatalog=RoomsCatalog(self.db_content['platforms_list'][i]['rooms'])
            j=self.roomsCatalog.findPos(room_ID)
            self.devicesCatalog=DevicesCatalog(self.db_content['platforms_list'][i]['rooms'][j]['devices'])
            self.devicesCatalog.insertValue(device_ID,dictionary)
   
    def setRoomParameter(self,platform_ID,room_ID,parameter,parameter_value):
        i=self.findPos(platform_ID)
        if i is not False:
            self.roomsCatalog=RoomsCatalog(self.db_content['platforms_list'][i]['rooms'])
            result=self.roomsCatalog.setParameter(room_ID,parameter,parameter_value)
            return result
        else:
            return False

    def removePlatform(self,platform_ID):
        i=self.findPos(platform_ID)
        if i is not False:
            self.db_content['platforms_list'].pop(i) 
            return True
        else:
            return i

    def removeRoom(self,platform_ID,room_ID):
        i=self.findPos(platform_ID)
        if i is not False:
            self.roomsCatalog=RoomsCatalog(self.db_content['platforms_list'][i]['rooms'])
            result=self.roomsCatalog.removeRoom(room_ID)
            return result
        else:
            return False

    def removeDevice(self,platform_ID,room_ID,device_ID):
        i=self.findPos(platform_ID)
        if i is not False:
            self.roomsCatalog=RoomsCatalog(self.db_content['platforms_list'][i]['rooms'])
            j=self.roomsCatalog.findPos(room_ID)
            self.devicesCatalog=DevicesCatalog(self.db_content['platforms_list'][i]['rooms'][j]['devices'])
            result=self.devicesCatalog.removeDevice(device_ID)
            return result
        else:
            return False

    def removeInactive(self,devices,inactiveTime):
        self.devicesCatalog=DevicesCatalog(devices)
        if self.devicesCatalog.removeInactive(inactiveTime):
            return True
        else:
            return False

    def dateUpdate(self,element):
        now=datetime.now()
        new_date=now.strftime("%d/%m/%Y/%H/%M")
        element['last_update']=new_date

    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.db_content,file, indent=4)
