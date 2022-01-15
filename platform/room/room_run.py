import json
import requests
import sys
import time

class RoomConfiguration(object):
    def __init__(self, filename, platform_ID):
        self.filename=filename
        self.platform_ID=platform_ID
        self.content=json.load(open(self.filename,"r"))
        self.serviceCatalogAddress=self.content['service_catalog']
        self.room_ID=self.content['room_info']['room_ID']
        self.room_name=self.content['room_info']['room_name']
        self.content["platform_ID"]=self.platform_ID
        self.save()
        self.timestamp=time.time()
            
    def findService(self,service):
        r=requests.get(self.serviceCatalogAddress+'/'+service).json()
        return r['url']

    def association(self):
        profilesAddress=self.findService('profiles_catalog')
        json_body={'platform_ID':self.platform_ID,'timestamp':self.timestamp}
        r=requests.put(f'{profilesAddress}/associateRoom/{self.platform_ID}',json=json_body)
        if r.status_code==200:
            for parameter in r.json()['msg']:
                self.content['room_info'][parameter]=r.json()['msg'][parameter]
            self.room_ID=r.json()['msg']['room_ID']
            self.room_name=r.json()['msg']['room_name']
            return True
        else:
            print(str(r.reason))
            return False
        
    def connection(self):
        try:
            resourcesAddress=self.findService('resource_catalog')
            server_msg={"room_ID":self.room_ID,"room_name":self.room_name,"devices":self.content['room_info']['devices']}
            r=requests.put(f'{resourcesAddress}/insertRoom/{self.platform_ID}',json=server_msg)
            self.content['room_info']['connection_flag']=True
            r.raise_for_status()
            return True
        except Exception as e:
            #print(e)
            return False
        
    def save(self):
        with open(self.filename,'w') as file:
            json.dump(self.content,file,indent=4)
            
if __name__ == '__main__':
    settings=sys.argv[1]
    platform_ID=sys.argv[2]
    room=RoomConfiguration(settings,platform_ID)
    if room.association():
        print(f"Association performed - {room.room_ID}: {room.room_name}")
        if room.connection():
            print("Resource connection performed. Saving...")
            room.save()
        else:
            print("Error connection.")
    print("Exiting...")
