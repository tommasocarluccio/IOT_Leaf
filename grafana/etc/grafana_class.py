import requests
import json
import time
import cherrypy
from etc.generic_service import *

#server_url="587f7d3d617a.ngrok.io"

class Grafana(Generic_Service):
    def __init__(self, conf_filename):
        Generic_Service.__init__(self,conf_filename)
        grafanaIP=self.retrieveService('grafana')["IP_address"]
        grafanaPORT=str(self.retrieveService('grafana')["port"])
        self.grafanaURL="http://"+grafanaIP+':'+grafanaPORT

    def createDashboard(self, platformID, roomID):
        clients_catalog=self.retrieveService('clients_catalog')
        print(clients_catalog)
        clients_result=requests.get(clients_catalog['url']+"/info/"+platformID+"/thingspeak").json()
        client=next((item for item in clients_result if item["room"] == roomID), False)
        channelID=str(client["channelID"])
        print(channelID)

        org_key=requests.get(clients_catalog['url']+"/info/"+platformID+"/grafana").json()["org_key"]
        print(org_key)
        headers= {
        "Authorization": "Bearer "+org_key,
        "Content-Type":"application/json",
        "Accept":"application/json"}

        url=self.grafanaURL+"/api/dashboards/db"
        new_dashboard_data=json.load(open('etc/default_dash.json'))
        new_dashboard_data["Dashboard"]["title"]=platformID+"_"+roomID
        new_dashboard_data["Dashboard"]["id"]=None
        new_dashboard_data["Dashboard"]["uid"]=platformID+roomID

        dash_string=json.dumps(new_dashboard_data)
        dash_string=dash_string.replace("xxxxxxx", channelID)
        new_dashboard_data=json.loads(dash_string)
        r=requests.post(url=url, headers=headers, json=new_dashboard_data, verify=False)
        print(r.json())
        if r.status_code==200:
            return True
        else:
            return False

    def deleteDashboard(self, platformID, roomID, org_key):
        headers= {
                "Authorization": "Bearer "+org_key,
                "Content-Type":"application/json",
                "Accept":"application/json"}
        
        url=self.grafanaURL+"/api/dashboards/uid/"+platformID+roomID
        r=requests.delete(url=url, headers=headers, verify=False)
        if r.status_code!=200:
            raise cherrypy.HTTPError(r.reason)

    def getDashboard(self, platformID, roomID):
        clients_catalog=self.retrieveService('clients_catalog')
        grafana_data=requests.get(clients_catalog['url']+"/info/"+platformID+"/grafana").json()
        org_key=grafana_data["org_key"]
        org_ID=grafana_data["org_ID"]
        url=self.grafanaURL+"/api/dashboards/uid/"+platformID+roomID
        headers= {
            "Authorization": "Bearer "+org_key,
            "Content-Type":"application/json",
            "Accept":"application/json"}
        r=requests.get(url=url, headers=headers, verify=False)
        print(r)
        if r.status_code==200:
            dashboard_data=r.json()
            return dashboard_data
        else:
            return False

    def changeDashboardName(self, platformID, roomID, new_name):
        dashboard_data=self.getDashboard(platformID, roomID)
        print(dashboard_data)
        if dashboard_data!=False:
            clients_catalog=self.retrieveService('clients_catalog')
            grafana_data=requests.get(clients_catalog['url']+"/info/"+platformID+"/grafana").json()
            org_key=grafana_data["org_key"]
            headers= {
            "Authorization": "Bearer "+org_key,
            "Content-Type":"application/json",
            "Accept":"application/json"}
            url=self.grafanaURL+"/api/dashboards/db"
            dashboard_data["dashboard"]["title"]=new_name
            r=requests.post(url=url, headers=headers, data=json.dumps(dashboard_data), verify=False)
            return True
        else:
            return False


    def retrieveDashInfo(self, platformID, roomID):
        notFound=1
        for org in self.orgContent["organizations"]:
            if org["org_name"]==platformID:
                for dash in org["dashboards"]:
                    if dash["uid"]==platformID+roomID:
                        notFound=0
                        dash_url=self.getDashboardURL(platformID, roomID)
                        return dash_url
        if notFound==1:
            return False

    def getDashboardURL(self, platformID, roomID):
        clients_catalog=self.retrieveService('clients_catalog')
        grafana_data=requests.get(clients_catalog['url']+"/info/"+platformID+"/grafana").json()
        org_key=grafana_data["org_key"]
        org_ID=grafana_data["org_ID"]
        profiles_catalog=self.retrieveService('profiles_catalog')
        room_name=requests.get(profiles_catalog['url']+"/"+platformID+"/rooms/"+roomID+"/preferences/room_name").json()
        self.changeDashboardName(platformID, roomID, room_name)
        headers= {
        "Authorization": "Bearer "+org_key,
        "Content-Type":"application/json",
        "Accept":"application/json"}
        uid=platformID+roomID
        url=self.grafanaURL+"/api/dashboards/uid/"+uid
        r=requests.get(url=url, headers=headers, verify=False)
        data=r.json()
        public_grafanaURL=requests.get(clients_catalog['url']+"/grafana/public").json()['url']
        try:
            dash_url=public_grafanaURL+data["meta"]["url"]+"?orgId="+org_ID
            return dash_url
        except:
            return False

    def getHomeURL(self, platformID):
        notFound=1
        for org in self.orgContent["organizations"]:
            if org["org_name"]==platformID:
                self.key=org["key"]
                self.orgID=str(org["orgId"])
                notFound=0
                break
        if notFound==0:
            self.home_url=self.server_url+"?orgId="+self.orgID
            return self.home_url
        else:
            return False
