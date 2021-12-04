import json
import time
import requests
import sys
import socket
import os

def get_ip_address():
     ip_address = '';
     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     s.connect(("8.8.8.8",80))
     ip_address = s.getsockname()[0]
     s.close()
     return ip_address

class RoomConfiguration(object):
    def __init__(self, filename, platform_ID):
        self.filename=filename
        self.platform_ID=platform_ID
        self.content=json.load(open(self.db_filename,"r"))
        self.serviceCatalogAddress=self.content['service_catalog']
        self.room_ID=self.content['room_info']['room_ID']
        self.room_name=self.content['room_info']['room_name']
        self.content["platform_ID"]=self.platform_ID
        
        #self.hubAddress="http://"+ get_ip_address()+":"+str(self.roomContent["hub_port"]) +"/hub"
        self.save()
        self.timestamp=time.time()
         

    def run(self):
        try:
            print("Connecting to Central HUB...")
            time.sleep(1)
            r=requests.get(self.hubAddress+'/hub_ID')
            if r.status_code==200:
                print("Connection performed.")
                self.hub_ID=r.json()
                self.serviceCatalogAddress=requests.get(self.hubAddress+'/service_catalog').json()
            else:
                print("Central HUB connection failed.\n")
        except IndexError as e:
            print(e)
            print("No Central HUB connection available.\n")
            
        
    def findService(self,service):
        r=requests.get(self.serviceCatalogAddress+'/public/'+service).json()
        return self.buildAddress(r.get('IP_address'),r.get('port'),r.get('service'))


    def buildAddress(self,IP,port,service):
        finalAddress=IP+service
        return finalAddress

    def association(self):
        try:
            profilesAddress=self.findService('profiles_catalog')
            json_body={'platform_ID':self.hub_ID,'timestamp':self.timestamp}
            r=requests.put(f'{profilesAddress}/associateRoom/{self.hub_ID}',json=json_body).json()
            if r['result'] is not False:
                self.roomContent['room_info']=r['result']
                self.room_ID=self.roomContent['room_info']['room_ID']
                self.room_name=self.roomContent['room_info']['room_name']
                return True
            else:
                return False
        except IndexError as e:
            print(e)
            return False
        
    def connection(self):
        try:
            resourcesAddress=self.findService('server_catalog')
            server_msg={"room_ID":self.room_ID,"room_name":self.room_name,"MRT":None,"Icl_clo":0.8,"M_met":1.2,"W_met":0,"devices":self.roomContent['room_info']['devices']}
            requests.put(f'{resourcesAddress}/insertRoom/{self.hub_ID}',json=server_msg)
            return True
        except:
            return False
        
    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.roomContent,file,indent=4)

if __name__ == '__main__':
    settings=sys.argv[1]
    platform_ID=sys.argv[2]
    room=RoomConfiguration(settings,platform_ID)
    room.run()
    if room.association():
        print(f"Association performed - {room.room_ID}: {room.room_name}")
        if room.connection():
            print("Server connection performed. Saving...")
            room.save()
        else:
            print("Error connection.")
    else:
        print("Association failed.")
    
    print("Exiting...")
    time.sleep(3)
    if room.roomContent['room_info']['connection_flag']:
        os.system("./sensors_autorun")

   

