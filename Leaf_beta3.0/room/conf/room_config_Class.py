import json
import requests
class RoomConfig(object):
    def __init__(self,room_filename):
        configuration=json.load(open(room_filename))
        self.serverURL=configuration['server']
        self.roomID=configuration['roomID']
        self.roomName=configuration['roomName']
        self.catalogID=configuration['catalogID']
        self.standardParameters=configuration['standard_parameters']
        self.thingSpeakURL=configuration['thingSpeakURL']
        self.devices=configuration['devices']
        self.basicURL=self.serverURL+'catalogs/'+self.catalogID
    def retrieveInfo(self):
        clientID=requests.get(self.basicURL+'/catalogID')
        broker=requests.get(self.basicURL+'/broker')
        self.broker=broker.json().get('addressIP')
        self.brokerPort=broker.json().get('port')
        self.clientID=clientID.json()
        