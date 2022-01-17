import json
from etc.generic_service import Generic_Service

class PlatformsCatalog():
    def __init__(self,db_filename):
        self.db_filename=db_filename
        self.content=json.load(open(self.db_filename,"r"))
        
    def set_value(self,platform_ID,field,value):
        platform=self.find_platform(platform_ID)
        platform[field]=value
        

    def add_chatID(self,platform_ID,chatID):
        platform=self.find_platform(platform_ID)
        try:
            chatID_list=platform['specs']['chatIDs']
            if chatID not in chatID_list:
                chatID_list.append(int(chatID))
        except:
            platform['specs']['chatIDs']=[]
            platform['specs']['chatIDs'].append(int(chatID))

        
    def find_platform(self,platform_ID):
        notFound=1
        for platform in self.content['platforms']:
            if platform['platform_ID']==platform_ID:
                notFound=0
                break
        if notFound==1:
            return False
        else:
            return platform

    def associate_room_thingspeak(self,platform_ID,room_ID):
        platform=self.find_platform(platform_ID)
        notFound=1
        if platform is not False:
            for spec in platform['specs']['thingspeak']:
                if spec['room'] is None:
                    spec['room']=room_ID
                    output="Available thingspeak channel found! Registered..."
                    notFound=0
                    break

            if notFound==1:
                output="No Available thingspeak channel!" 
            return output
        else:
            return False

    def removePlatform(self,platform_ID):
        self.set_value(platform_ID,"associated",False)
        self.remove_all_rooms(platform_ID)

    def removeRoom(self,platform_ID,room_ID):
        notFound=1
        platform=self.find_platform(platform_ID)
        if platform is not False:
            for spec in platform['specs']['thingspeak']:
                if spec['room'] ==room_ID:
                    spec['room']=None
                    notFound=0
                    return True
            if notFound==1:
                return False
        else:
            return False

    def remove_all_rooms(self,platform_ID):
        platform=self.find_platform(platform_ID)
        platform['specs']['chatIDs'].clear()
        for spec in platform['specs']['thingspeak']:
            self.removeRoom(platform_ID,spec['room'])

    def remove_chatID(self,platform_ID,chatID):
        platform=self.find_platform(platform_ID)
        chatID_list=platform['specs']['chatIDs']
        chatID_list.remove(chatID)

    def save(self):
        with open(self.db_filename,'w') as file:
            json.dump(self.content,file, indent=4)
        
class UsersCatalog():
    def __init__(self, db_filename):
        self.db_filename=db_filename
        self.content=json.load(open(self.db_filename,"r"))
        self.createDict()
        
    def createDict(self):
        d = self.content['users']
        self.userpassdict = dict((i["username"],["password"]) for i in d)
        
    def find_user(self,username):
        notFound=1
        for user in self.content['users']:
            if user.get('username').lower()==username.lower():
                notFound=0
                break
        if notFound==1:
            return False
        else:
            return user
        
    def login(self,username,password):
        user=self.find_user(username)
        if user is not False and user['password']==password:
            return user
        else:
            return False  
        
    def removePlatform(self,username,platform_ID):
        user=self.find_user(username)
        if user is not False:
            try:
                user['platforms_list'].remove(platform_ID)
                return True
            except Exception as e:
                return False
        else:
            return False
    
    def removeUser(self,username):
        try:
            self.content['users'].remove(user)
            return True
        except Exception as e:
            return False

    def save(self):
        self.createDict()
        with open(self.db_filename,'w') as file:
            json.dump(self.content,file, indent=4)
    

class ClientsCatalog(Generic_Service):
    def __init__(self, conf_filename,users_filename="database/users.json",platforms_filename="database/platforms.json"):
        Generic_Service.__init__(self,conf_filename)
        self.users_filename=users_filename
        self.platforms_filename=platforms_filename
        self.users=UsersCatalog(self.users_filename)
        self.platforms=PlatformsCatalog(self.platforms_filename)
        
    def check_registration(self,username,platform_ID):
        if self.users.find_user(username) is not False:
            return "user"
        platform=self.platforms.find_platform(platform_ID)
        if platform is not False:
            if platform['associated']:
                return "associated"
            else:
                return False
        else:
            return "platform"
        
    def check_association(self,platform_ID):
        platform=self.platforms.find_platform(platform_ID)
        return platform['associated']
            
        
            
            
        









