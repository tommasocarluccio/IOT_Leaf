import json


class ClientsCatalog():
    def __init__(self, db_filename):
        self.db_filename=db_filename
        self.clientsContent=json.load(open(self.db_filename,"r"))
        self.createDict()

    def createDict(self):
        d = self.clientsContent['platforms']
        self.userpassdict = dict((i["user"]["username"],i["user"]["password"]) for i in d)
        
    def find_platform(self,platform_ID):
        notFound=1
        for i in range(len(self.clientsContent['platforms'])):
            if self.clientsContent['platforms'][i]['platform_ID']==platform_ID:
                notFound=0
                break
        if notFound==1:
            return False
        else:
            return self.clientsContent['platforms'][i]
        
    def find_user(self,username):
        notFound=1
        for platform in self.clientsContent['platforms']:
            if platform['user'].get('username')==username:
                notFound=0
                break
        if notFound==1:
            return False
        else:
            return platform
        
    def removePlatform(self,platform_ID):
        platform=self.find(platform_ID)
        if platform is not False:
            self.clientsContent['platforms'].remove(platform_ID)
            return True
        else:
            return False
        

    def save(self):
        self.createDict()
        with open(self.db_filename,'w') as file:
            json.dump(self.clientsContent,file, indent=4)









