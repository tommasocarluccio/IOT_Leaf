import json
import requests
import sys

class Catalog():
    def __init__(self,settings):
        self.settings=settings
        self.myCatalog= json.load(open(settings)) # Read the JSON into the buffer
        #jsonFile.close() # Close the JSON file
        self.catalogID=self.myCatalog['catalogID']
        self.inactiveTime=self.myCatalog['inactiveTime']
        self.clientID=self.myCatalog['clientID']
        self.serverAddress=self.myCatalog['server']
        self.brokerIP=self.myCatalog['broker'][0].get('addressIP')
        self.brokerPort=self.myCatalog['broker'][0].get('port')
        self.brokerAddress={"addressIP":self.brokerIP,"port":self.brokerPort}
        self.rooms=self.myCatalog['rooms']
    def run(self):
        self.putBody={'catalogID':self.catalogID,'inactiveTime':self.inactiveTime,'clientID':self.clientID,'broker':self.brokerAddress,'rooms':self.rooms}
    def pingDatabase(self):
        try:
            r=requests.put('http://127.0.0.1:8080'+'/leaf/'+'insertCatalog/'+self.catalogID, json=self.putBody)
            if r.status_code==200:
                output="{} - Connection performed".format(self.catalogID)
                print(output)
            else:
                print("Database connection failed: Catalog not inserted\n")
        except:
            print("Error detected\n")
            
        
    

if __name__ == '__main__':
    settings=sys.argv[1]
    catalog=Catalog(settings)
    catalog.run()
    print("\n%% Running Catalogue %%\n")
    catalog.pingDatabase()
    

