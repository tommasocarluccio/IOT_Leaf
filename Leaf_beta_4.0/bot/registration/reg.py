import cherrypy
import json
import os
import sys
sys.path.append('/home/pi/Desktop/Leaf/Leaf_beta_v2/bot')

class Registration_deployer(object):
    exposed=True
    def GET(self,*uri,**params):
        if (len(uri))>0 and uri[0]=="reg.html":
            return open('reg.html')

        elif (len(uri)>0 and uri[0]=="reg_results"):
            users=json.load(open('reg.json'))
            for user in users.get("users"):
                if user['user_ID']==params['userID']:
                    return open("fail_reg_user.html") 
            if params['psw']!=params['psw-repeat']:
                return open("fail_reg_pass.html") 

            else:
                users["users"].append({
                    "user_ID":params['userID'],
                    "catalog_id":params['catalogID'],
                    "password":params['psw']
                    })
                with open('reg.json', 'w') as outfile:
                    json.dump(users, outfile, indent=4)
            
                return open("correct_reg.html")

if __name__ == '__main__':
    configuration=json.load(open("../etc/bot_configuration.json"))
    regURL=configuration['registration'][0].get('addressIP')
    regPort=configuration['registration'][0].get('port')
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.sessions.on': True
        }
    }
    
    cherrypy.tree.mount(Registration_deployer(), '/', conf)
    cherrypy.config.update({'server.socket_host': regURL})
    cherrypy.config.update({'server.socket_port': regPort}) 
    cherrypy.engine.start()
    cherrypy.engine.block()
