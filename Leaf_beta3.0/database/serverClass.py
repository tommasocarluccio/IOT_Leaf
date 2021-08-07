import json
from datetime import datetime
import time

class NewCatalog():
    def __init__(self,catalogID,inactiveTime,clientID,broker,lastUpdate,rooms):
        self.catalogID=catalogID
        self.inactiveTime=inactiveTime
        self.clientID=clientID
        self.broker=broker
        self.lastUpdate=lastUpdate
        self.rooms=rooms
        
    def jsonify(self):
        room={'catalogID':self.catalogID,'inactiveTime':self.inactiveTime,'clientID':self.clientID,'clientID':self.clientID,'broker':self.broker,'rooms':self.rooms,'last_update':self.lastUpdate}
        return room
    
class Server():
    def __init__(self,myDatabase,databaseFileName):
        self.databaseFileName=databaseFileName
        self.myDatabase=myDatabase
        
    def retrieveOwner(self):
        owner=self.myDatabase["database_owner"]
        return owner
    
    def retrieveAllClients(self):
        clients=self.myDatabase["clients"]
        return clients
    
    def retrieveClientsList(self):
        clientsList=[]
        for catalog in self.myDatabase['clients']:
            clientsList.append(catalog['catalogID'])
        return clientsList
    
    def retrieveCatalogID(self, catalogID):
        notFound=1
        for catalog in self.myDatabase['clients']:
            if str(catalog['catalogID']) ==(catalogID):
                notFound=0
                return catalog
        if notFound==1:
                    return False
        
    def insertCatalog(self,catalogID,inactiveTime,clientID,broker,rooms):
        notExisting=1
        now=datetime.now()
        timestamp=now.strftime("%d/%m/%Y %H:%M")
        catalog=self.retrieveCatalogID(catalogID)
        if catalog is False:
            newCatalog=NewCatalog(catalogID,inactiveTime,clientID,broker,timestamp,rooms).jsonify()
            self.myDatabase['clients'].append(newCatalog)
            return True
        else:
            return False
        
    def save(self,databaseFileName):
        with open(databaseFileName,'w') as file:
            json.dump(self.myDatabase,file, indent=4)
    