import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import emoji
import requests
import json
import numpy as np
import sys
import cherrypy
from etc.generic_service import *

class LeafBot(Generic_Service):
    exposed=True

    def __init__(self, configuration_file):
        Generic_Service.__init__(self,configuration_file, False)
        self.service=self.registerRequest()

        self.conf_content=json.load(open(configuration_file,"r"))
        self.serviceURL=self.conf_content['service_catalog']
        self.clientURL=requests.get(self.serviceURL+'/clients_catalog/public').json()['url']
        print(self.clientURL)

        self.api_coordinates_url='http://api.waqi.info/feed/geo:'
        self.api_city_url='http://api.waqi.info/feed/'

        tokens=requests.get(self.clientURL+'/temp_tokens').json()
        self.tokenBot=tokens['tokens']['telegram_token']
        self.tokenApi=tokens['tokens']['weather_api_token']

        self.bot = telepot.Bot(self.tokenBot)
        self.authentications=[]
        self.thresholds=[]

        self.keyboards()
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()

        self.users_data={"users": []}

        self.aqi_state_dict=[
            {
            "circle":":green_circle:",
            "status":"GOOD"
            },
            {
            "circle":":yellow_circle:",
            "status":"MODERATE"
            },
            {
            "circle":":orange_circle:",
            "status":"UNHEALTHY for Sensitive Groups"
            },
            {
            "circle":":red_circle:",
            "status":"UNHEALTHY"
            },
            {
            "circle":":purple_circle:",
            "status":"VERY UNHEALTHY"
            },
            {
            "circle":":brown_circle:",
            "status":"HAZARDOUS"
            },
            {
            "circle":":white_circle:",
            "status":"Unavailable"
            }
            ]

        self.emoji_dic={
            "temperature":":thermometer:",
            "humidity":":droplet:",
            "AQI":":cyclone:",
            "Bedroom":":zzz:",
            "Kitchen":":fork_and_knife:",
            "Bathroom":":bathtub:"
            }
    
        self.unit_dict={
            "temperature":"°C",
            "humidity":"%",
        }
    
    def create_new_user(self, chat_ID):
        user={
            "chat_ID":chat_ID,
            "user_ID":None,
            "platform_ID":None,
            "room_ID":None,
            "flags":
                {
                    "userID_flag":0,
                    "password_flag":0,
                    "insert_city_flag":0,
                    'platform_name_flag':0,
                    'new_room_flag':0,
                    'remove_room_flag':0,
                    'room_name_flag':0,
                    'thresholds_flag':0,
                    'new_platform_flag':0,
                    'remove_platform_flag':0
                }
            }
        return user

    def set_location(self, chat_ID, message, coordinates):
        profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
        adaptorURL=requests.get(self.serviceURL+'/database_adaptor').json()['url']

        #check in the db user with the current chatID
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        print("user: ", user)
        if coordinates==True:
            url=self.api_coordinates_url+str(message['latitude'])+';'+str(message['longitude'])+'/?token='+self.tokenApi
        else:
            url=self.api_city_url+message+'/?token='+self.tokenApi
        try:
            api_data=requests.get(url).json()
            body_profile={
                "parameter":"coord",
                "parameter_value": {"lat": api_data['data']['city']['geo'][0],"long": api_data['data']['city']['geo'][1]}
            }

            meta=str(api_data['data']['city']['name'])
            body={
            "latitude":api_data['data']['city']['geo'][0],
            "longitude":api_data['data']['city']['geo'][1],
            "metadata":meta
            }
            if user['room_ID']==None:
                generic_room=requests.get(profileURL+'/'+user['platform_ID']+'/rooms').json()[0]['room_ID']
            else:
                generic_room=user['room_ID']
            print(generic_room)
            print(adaptorURL+'/'+user['platform_ID']+'/uploadLocation')
            requests.post(profileURL+'/setParameter/'+user['platform_ID'], json=body_profile)
            requests.put(adaptorURL+'/'+user['platform_ID']+'/'+generic_room+'/uploadLocation', json=body, headers={})
            return api_data['data']['city']
        except:
            return False

    def get_external_conditions(self, chat_ID):
        #check in the db user with the current chatID
        profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        coordinates=requests.get(profileURL+'/'+user['platform_ID']+'/coord').json()
        url=self.api_coordinates_url+str(coordinates['lat'])+';'+str(coordinates['long'])+'/?token='+self.tokenApi

        try:
            api_data=requests.get(url).json()
            timestamp=api_data['data']['time']['s']
            date=timestamp.split(' ')[0]
            time=timestamp.split(' ')[1]
            aqi=api_data["data"]["aqi"]
            try:
                pm25=api_data['data']['iaqi']['pm25']['v']
            except:
                pm25='-Unavailable-'
            try:
                pm10=api_data['data']['iaqi']['pm10']['v']
            except:
                pm10='-Unavailable-'
            temp=api_data['data']['iaqi']['t']['v']
            humidity=api_data['data']['iaqi']['h']['v']
            vap_pres=(humidity/100)*6.105*np.exp(17.27*((temp)/(237+temp)))
            try:
                wind=api_data['data']['iaqi']['w']['v']
                app_temp=temp+0.33*(vap_pres)-(0.7*wind)-4
            except:
                wind='-Unavailable-'
                app_temp=temp+0.33*(vap_pres)-4
            ext_data={
                "date":date,
                "time":time,
                "aqi":aqi,
                "pm25":pm25,
                "pm10":pm10,
                "temp":temp,
                "humidity":humidity,
                "wind":wind,
                "app_temp":app_temp
            }
            return ext_data
        except:
            print("Error retrieving data")
            return False

    def get_general_info(self, chat_ID):
        profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
        resourceURL=requests.get(self.serviceURL+'/resource_catalog').json()['url']
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        profile_info=requests.get(profileURL+'/'+user['platform_ID']).json()
        output='Your Leaf device:\n:bust_in_silhouette:'+profile_info['platform_ID']+':\t'+profile_info['platform_name']+'\n'
        output+=':round_pushpin:Location coordinates:\t'+str(profile_info['coord']['lat'])+', '+str(profile_info['coord']['long'])+'\n'
        try:
            output+=':alarm_clock:Last update:\t'+profile_info['last_update']+'\n'
        except:
            pass
        output+='Rooms:\n'
        if profile_info['rooms']!=[]:
            for room in profile_info['rooms']:
                try:
                    emo_room=self.emoji_dic[room['preferences']['room_name']]
                except:
                    emo_room=':house:'
                if room['connection_flag']==1:
                    output+=emo_room+room['preferences']['room_name']+':\n'
                    output+='Devices:\n'
                    devices=requests.get(resourceURL+'/'+user['platform_ID']+'/'+room['room_ID']+'/devices').json()
                    for device in devices:
                        output+=':arrow_forward:'+device['deviceID']+' (last alive: '+device['date']+')\n'
                else:
                    output+=emo_room+room['preferences']['room_name']+' (not yet associated)\n'               
        else:
            output+='No room detected.\n'
        return output

    def add_room(self, chat_ID, room_name):
        profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        room_body={
            "room_name":room_name
        }
        print(room_body)
        log=requests.put(profileURL+'/insertRoom/'+user['platform_ID'], json=room_body, headers={}).json()
        print(log)
        if log:
            return True
        else:
            return False

    def create_rooms_keyboard(self, chat_ID):
        profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        rooms_info=requests.get(profileURL+'/'+user['platform_ID']+'/rooms').json()
        room_list_keyboard=[]
        for room in rooms_info:
            room_name=room['preferences']['room_name']
            try:
                emo=self.emoji_dic[room_name]
            except:
                emo=':small_blue_diamond:'
            room_list_keyboard+=[[InlineKeyboardButton(text=emoji.emojize(f"{emo}\t{room_name}", use_aliases=True), callback_data=room_name)]]
        rooms_keyboard=InlineKeyboardMarkup(inline_keyboard=room_list_keyboard)
        return rooms_keyboard

    def create_parameters_keyboard(self, chat_ID):
        profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        room_info=requests.get(profileURL+'/'+user['platform_ID']+'/rooms/'+user['room_ID']).json()
        parameters_list_keyboard=[]
        for parameter in room_info['preferences']['thresholds'].keys():
            try:
                emo=self.emoji_dic[parameter]
            except:
                emo=':small_blue_diamond:'
            parameters_list_keyboard+=[[InlineKeyboardButton(text=emoji.emojize(f"{emo}\t{parameter}", use_aliases=True), callback_data=parameter)]]
        parameters_keyboard=InlineKeyboardMarkup(inline_keyboard=parameters_list_keyboard)
        return parameters_keyboard

    def create_platforms_keyboard(self, chat_ID):
        profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        platforms_list=requests.get(self.clientURL+'/platforms_list'+'?username='+user['user_ID']).json()
        plt_list_keyboard=[]
        emo=':small_blue_diamond:'
        for i in platforms_list:
            try:
                platform_name=self.get_platform_name(chat_ID, i)
            except:
                platform_name=i
            plt_list_keyboard=plt_list_keyboard+[[InlineKeyboardButton(text=emoji.emojize(f'{emo}\t{i}\t({platform_name})', use_aliases=True), callback_data=i)]]
        plt_list_keyboard=plt_list_keyboard+[[InlineKeyboardButton(text=emoji.emojize(':heavy_plus_sign:\tAdd a new platform', use_aliases=True), callback_data='new_platform')]]
        rlk=InlineKeyboardMarkup(inline_keyboard=plt_list_keyboard)
        return rlk

    def get_room_measures(self, chat_ID, room_ID):
        adaptorURL=requests.get(self.serviceURL+'/database_adaptor').json()['url']
        #check in the db user with the current chatID
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        room_data=requests.get(adaptorURL+'/'+user['platform_ID']+'/'+room_ID+'/now').json()
        date=room_data["created_at"][0].split("T")[0]
        time=room_data["created_at"][0].split("T")[1].split("Z")[0]
        room_name=self.get_room_name(chat_ID, room_ID)
        try:
            room_emo=self.emoji_dic[room_name]
        except:
            room_emo=':small_blue_diamond:'
        output=f'{room_emo} {room_name}\nLast update: {date} at {time}\n'
        for key, value in room_data.items():
            if key!='created_at' and key!='entry_id':
                try:
                    emo=self.emoji_dic[value[0]]
                except:
                    emo=':small_blue_diamond:'
                try:
                    unit=self.unit_dict[value[0]]
                except:
                    unit=''
                try:
                    if self.check_values(chat_ID, room_ID, value[0], value[1]):
                        warning_emo=":warning:"
                    else:
                        warning_emo=""
                except:
                    warning_emo=""
                output+=emo+' '+value[0]+': '+str(value[1])+' '+unit+'  '+warning_emo+'\n'
        return output

    def check_values(self, chat_ID, room_ID, param, value):
        th=self.get_thresholds(chat_ID, room_ID, param, False)
        if float(value)<=th["max"] and float(value) >=th["min"]:
            return False 
        else:
            return True #return True when value is outside the thresholds

    def get_thresholds(self, chat_ID, room_ID, param, optimal):
        profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        if optimal:
            th=requests.get(profileURL+'/'+user["platform_ID"]+'/rooms/'+room_ID+'/preferences/optimal').json()[param]
        else:
            th=requests.get(profileURL+'/'+user["platform_ID"]+'/rooms/'+room_ID+'/preferences/thresholds').json()[param]
        return th

    def get_home_measures(self, chat_ID):
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        rooms_list=requests.get(self.clientURL+'/associated_rooms/'+user['platform_ID']+'/thingspeak').json()
        platform_name=self.get_platform_name(chat_ID, user["platform_ID"])
        output=f':house:Current condition in {platform_name}:\n\n'
        for room in rooms_list:
            try:
                room_output=self.get_room_measures(chat_ID, room)
                output+=room_output+'\n'
            except: pass
        return output

    def get_statistics(self, chat_ID, period):
        statisticsURL=requests.get(self.serviceURL+'/statistics_catalog').json()['url']
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        room_name=self.get_room_name(chat_ID, user['room_ID'])
        output=f'Statistics for {room_name} for the last {period}\n'
        log=requests.get(statisticsURL+'/'+user['platform_ID']+'/'+user['room_ID']+'/'+period).json()
        for key, value in log.items():
            if key=='temp':
                key='temperature'
            elif key=='hum':
                key='humidity'
            try:
                emo=self.emoji_dic[key]
            except:
                emo=':small_blue_diamond:'
            try:
                unit=self.unit_dict[key]
            except:
                unit=''
            output+=emo+key+'\n'
            if value['min']=='no_data':
                output+='\t'+'Min'+': '+value['min']+'\n'
            else:
                output+='\t'+'Min'+': '+str(round(value['min'], 2))+' '+unit+'\n'
            if value['max']=='no_data':
                output+='\t'+'Max'+': '+value['max']+'\n'
            else:
                output+='\t'+'Max'+': '+str(round(value['max'], 2))+' '+unit+'\n'
            if value['avg']=='no_data':
                output+='\t'+'Average'+': '+value['avg']+'\n'
            else:
                if value['Advice']!="not enough data":
                    output+='\t'+'Average'+': '+str(round(value['avg'], 2))+' '+unit+'\n' + ":memo:"+value['Advice']+"\n\n"
                else:
                    output+='\t'+'Average'+': '+str(round(value['avg'], 2))+' '+unit+'\n'
        return output
     
    def get_room_name(self, chat_ID, room_ID):
        profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        return requests.get(profileURL+'/'+user['platform_ID']+'/rooms/'+room_ID+'/preferences/room_name').json()
    
    def get_platform_name(self, chat_ID, platform_ID):
        profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False)
        return requests.get(profileURL+'/'+platform_ID).json()["platform_name"]

    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)

        #check in the db user with the current chatID
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False) 
        #if first time this chat_ID is used a new user is created
        if user==False:
            print("New user!")
            user=self.create_new_user(chat_ID)
            self.users_data['users'].append(user)
        print(user)
        if content_type=='text':
            message = msg['text']
            if message=='/start':
                self.bot.sendMessage(chat_ID, emoji.emojize(':seedling:\t Welcome to Leaf!\t:seedling:\nBefore starting Log into your Leaf account or create one', use_aliases=True), reply_markup=self.login_keyboard)
                user["user_ID"]=None
                user["platform_ID"]=None
                user["room_ID"]=None

            elif message=='/home':
                self.bot.sendMessage(chat_ID, emoji.emojize(f':seedling:\tWelcome to Leaf!\t:seedling:\nYou are logged in as {user["user_ID"]}', use_aliases=True))
                self.bot.sendMessage(chat_ID, 'Select an option:', reply_markup=self.home_keyboard)
                user['flags']=dict.fromkeys(user['flags'], 0)
            
            elif message=='/logout':
                self.bot.sendMessage(chat_ID, emoji.emojize(':seedling:\t Welcome to Leaf!\t:seedling:\nBefore starting Log into your Leaf account or create one', use_aliases=True), reply_markup=self.login_keyboard)
                platforms_list=requests.get(self.clientURL+'/platforms_list'+'?username='+user['user_ID']).json()
                user['flags']=dict.fromkeys(user['flags'], 0)
                for platform in platforms_list:
                    log=requests.delete(self.clientURL+'/removeChatID/'+str(platform)+'/'+str(chat_ID))
                user["user_ID"]=None
                user["platform_ID"]=None
                user["room_ID"]=None
            #user has written their userID
            elif user['flags']['userID_flag']==1 and user['flags']['password_flag']==0:
                self.bot.sendMessage(chat_ID, f'Now type your password for {message}:', reply_markup=self.back_login)
                #create a provisional instance to store that userID with correspondent chatID
                user_dict={"chat_ID":chat_ID,
                "user_ID":message
                }
                self.authentications.append(user_dict)
                user['flags']['password_flag']=1
                print('Auth: ', self.authentications)
            #user has written their password
            elif user['flags']['userID_flag']==1 and user['flags']['password_flag']==1:
                #extract provitional instance to retrieve inserted userID
                user_auth=next((item for item in self.authentications if item["chat_ID"] == chat_ID), False)
                password=message
                ##check password-userID
                log=requests.post(self.clientURL+'/login',json={"username":user_auth['user_ID'],'password':password,'chat_ID':str(chat_ID)})
                #if all correct
                if log.status_code==200:
                    user['user_ID']=user_auth['user_ID']
                    self.bot.sendMessage(chat_ID, emoji.emojize(f':seedling:\tWelcome to Leaf!\t:seedling:\nYou are logged in as {user["user_ID"]}', use_aliases=True))
                    keyboard=self.create_platforms_keyboard(chat_ID)
                    self.bot.sendMessage(chat_ID, 'Choose the registered platform you want to visualize or register a new one', reply_markup=keyboard)

                else:
                    self.bot.sendMessage(chat_ID, f'Wrong username or password!\nPlease try again', reply_markup=self.login_keyboard)
                user['flags']['userID_flag']=0
                user['flags']['password_flag']=0
                self.authentications=[i for i in self.authentications if i['chat_ID']!=chat_ID]

            #user has written the new city
            elif user['flags']['insert_city_flag']==1:
                api_data=self.set_location(chat_ID, message, False)
                if api_data!=False:
                    self.bot.sendMessage(chat_ID, 'Your location has been Succesfully updated!')
                    self.bot.sendMessage(chat_ID, f"The nearest active station found is: {api_data['name']}")
                    self.bot.sendMessage(chat_ID, 'Select an option:', reply_markup=self.home_keyboard)
                    print("New nearest station found: "+ api_data['name'])
                    user['flags']['insert_city_flag']=0
                else:
                    self.bot.sendMessage(chat_ID, 'Invalid city name! Please try again')
                    self.bot.sendMessage(chat_ID, 'Type on your keyboard the city name:')
            #user has written new name for platform
            elif user['flags']['platform_name_flag']==1:
                profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
                body_profile={
                    "parameter":"platform_name",
                    "parameter_value":message
                }
                log=requests.post(profileURL+'/setParameter/'+user['platform_ID'], json=body_profile)
                if log.status_code==200:
                    self.bot.sendMessage(chat_ID, 'Update succesfull!')
                    self.bot.sendMessage(chat_ID, f'Your new platform name is: {message}', reply_markup=self.home_keyboard)
                else:
                    self.bot.sendMessage(chat_ID, 'Update was unsuccesfull! Please try again', reply_markup=self.home_keyboard)
                user['flags']['platform_name_flag']=0
            #user has written new room 
            elif user['flags']['new_room_flag']==1:
                if self.add_room(chat_ID, message):
                    self.bot.sendMessage(chat_ID, f'A new instance for the room {message} has been added to the platform!', reply_markup=self.home_keyboard)
                else:
                    self.bot.sendMessage(chat_ID, 'unsuccesfull operation! Please try again.', reply_markup=self.home_keyboard)
                user['flags']['new_room_flag']=0
            #user has written new name for room
            elif user['flags']['room_name_flag']==1:
                profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
                body_profile={
                    "room_name":message
                }
                log=requests.post(profileURL+'/setRoomParameter/'+user['platform_ID']+'/'+user['room_ID'], json=body_profile)
                if log.status_code==200:
                    self.bot.sendMessage(chat_ID, 'Update succesfull!')
                    self.bot.sendMessage(chat_ID, f'Your new Room name is: {message}', reply_markup=self.home_keyboard)
                else:
                    self.bot.sendMessage(chat_ID, 'Update was unsuccesfull! Please try again', reply_markup=self.home_keyboard)
                user['flags']['room_name_flag']=0
            #user has written new thresholds for a parameter in a room
            elif user['flags']['thresholds_flag']==1:
                min_th=float(message.split(" ")[0])
                max_th=float(message.split(" ")[1])
                if min_th>max_th:
                    self.bot.sendMessage(chat_ID, 'The minimum cannot be greater than the maximum value! Please try again!', reply_markup=self.room_menu)
                    user['flags']['thresholds_flag']=0
                try:
                    profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
                    parameter=next((item['parameter'] for item in self.thresholds if item["chat_ID"] == chat_ID), False)
                    body_profile={
                        "thresholds":{
                            parameter:{
                            "min":min_th,
                            "max":max_th
                            }
                        }
                    }
                    log=requests.post(profileURL+'/setRoomParameter/'+user['platform_ID']+'/'+user['room_ID'], json=body_profile)
                    if log.status_code==200:
                        self.bot.sendMessage(chat_ID, 'Update succesfull!')
                        self.bot.sendMessage(chat_ID, f'Your new thresholds for {parameter} are: {min_th},{max_th}', reply_markup=self.room_menu)
                    else:
                        self.bot.sendMessage(chat_ID, f'{log.reason} Please try again', reply_markup=self.room_menu)
                    user['flags']['thresholds_flag']=0
                    self.thresholds=[i for i in self.thresholds if i['chat_ID']!=chat_ID]
                except:
                    self.bot.sendMessage(chat_ID, 'Update was unsuccesfull! Please try again', reply_markup=self.room_menu)
                    user['flags']['thresholds_flag']=0
                    self.thresholds=[i for i in self.thresholds if i['chat_ID']!=chat_ID]
            #user has written new platform
            elif user['flags']['new_platform_flag']==1:
                body={
                    'username':user['user_ID'],
                    'platformID':message
                }
                log=requests.put(self.clientURL+'/newPlatform', json=body)
                keyboard=self.create_platforms_keyboard(chat_ID)
                if log.status_code==200:
                    self.bot.sendMessage(chat_ID, 'Your new platform has been correctly associated!', reply_markup=keyboard)
                else:
                    self.bot.sendMessage(chat_ID, f"{log.reason}", reply_markup=keyboard)
                user['flags']['new_platform_flag']=0
            
            elif message=='/help':
                self.bot.sendMessage(chat_ID, emoji.emojize(':black_circle:\tUse the displayed keyboards to navigate through the bot functions\n'
                                     ':black_circle:\tUse the "Set your Location" button to change the previously registered location and access the data of the nearest available station through the "Current Condition" menù\n'
                                     ,use_aliases=True), reply_markup=self.back_button)

            else:
                self.bot.sendMessage(chat_ID ,'Invalid command!\n'
                                 'To go to the main menu use : /home\n'
                                 'To get help use: /help')
            
        elif content_type=='location':
            location=msg['location']
            api_data=self.set_location(chat_ID, location, True)
            if api_data!=False:
                self.bot.sendMessage(chat_ID, 'Your location has been Succesfully updated!', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                self.bot.sendMessage(chat_ID, f'The nearest active station found is: {api_data["name"]}')
                self.bot.sendMessage(chat_ID, 'Select an option:', reply_markup=self.home_keyboard)
                print('New nearest station found: '+ api_data['name'])
            else:
                self.bot.sendMessage(chat_ID, 'Error in sending location! Please try again', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
                self.bot.sendMessage(chat_ID, 'Push the button to share your location', reply_markup=self.location_keyboard)

        self.users_data['users']=[user if x['chat_ID']==chat_ID else x for x in self.users_data['users']]
        
    def keyboards(self):

        self.login_keyboard= InlineKeyboardMarkup (inline_keyboard=[
                    [InlineKeyboardButton(text=emoji.emojize(':gear: LOGIN', use_aliases=True), callback_data='login')],
                    [InlineKeyboardButton(text=emoji.emojize(':green_circle:Register on the website:green_circle:', use_aliases=True), url=self.clientURL+"/reg")],
                    ])

        self.back_login=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back_login')]
                    ])


        self.starting_keyboard=InlineKeyboardMarkup (inline_keyboard=[
                    [InlineKeyboardButton(text=emoji.emojize(':gear: Settings', use_aliases=True), callback_data='set')],
                    [InlineKeyboardButton(text=emoji.emojize(':house: Go to the main menu', use_aliases=True), callback_data= 'home')],
                    ])


        self.settings_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= emoji.emojize(':globe_with_meridians: Location settings', use_aliases=True), callback_data='set_loc'),
                InlineKeyboardButton(text= emoji.emojize(':computer: System settings', use_aliases=True), callback_data='set_dev')],
                [InlineKeyboardButton(text= emoji.emojize(':question: Get info on your device', use_aliases=True), callback_data='info_dev')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

        self.home_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text= emoji.emojize(':watch: Current Conditions', use_aliases=True), callback_data='act'),
                    InlineKeyboardButton(text= emoji.emojize(':key: Enter a Room', use_aliases=True), callback_data='room')],
                    [InlineKeyboardButton(text=emoji.emojize(':green_book: Tips', use_aliases=True), callback_data='tips'),
                    InlineKeyboardButton(text=emoji.emojize(':gear: Settings',use_aliases=True), callback_data='set')],
                    [InlineKeyboardButton(text=emoji.emojize(':arrows_counterclockwise: Change active Platform', use_aliases=True), callback_data='active_platform')]
                    ])


        self.location_opt_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':round_pushpin:\tSend your current position', use_aliases=True), callback_data='send_loc')],
                [InlineKeyboardButton(text=emoji.emojize(':cityscape:\tInsert City', use_aliases=True), callback_data='insert_city')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])


        self.device_setting=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= emoji.emojize(':house: Add a new room', use_aliases=True), callback_data='add_room'),
                InlineKeyboardButton(text= emoji.emojize(':heavy_multiplication_x: Remove a room', use_aliases=True), callback_data='remove_room')],
                [InlineKeyboardButton(text= emoji.emojize(':pencil2: Change platform name', use_aliases=True), callback_data='change_platform_name'),
                InlineKeyboardButton(text= emoji.emojize(':heavy_multiplication_x: Remove a platform', use_aliases=True), callback_data='remove_platform')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])


        self.back_button=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                    ])

        self.actual_menu=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= emoji.emojize(':house: Internal Conditions', use_aliases=True), callback_data='act_int'),
                InlineKeyboardButton(text= emoji.emojize(':earth_africa: External Conditions', use_aliases=True), callback_data='act_ext')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

        self.other_tip_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':pencil: Another Tip!', use_aliases=True), callback_data='other_tips'),
                InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

        self.location_keyboard=ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Send your location', request_location=True)]
                ])

        self.back_or_home=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')],
                [InlineKeyboardButton(text=emoji.emojize(':house: Go to the main menu', use_aliases=True), callback_data= 'home')],
                ])


        self.room_menu=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text= emoji.emojize(':bar_chart: Room analytics', use_aliases=True), callback_data='stat'),
                    InlineKeyboardButton(text= emoji.emojize(':gear: Room settings', use_aliases=True), callback_data='room_set')],
                    [InlineKeyboardButton(text=emoji.emojize(':watch: Room Current conditions', use_aliases=True), callback_data='room_act')],
                    [InlineKeyboardButton(text=emoji.emojize(':house: Go to the main menu', use_aliases=True), callback_data='home')]
                    ])

        self.room_set_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':pencil2: Change room name', use_aliases=True), callback_data='change_room_name')],
                [InlineKeyboardButton(text=emoji.emojize(':radio_button: Change room thresholds', use_aliases=True), callback_data='change_thresholds')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])
        

    def on_callback_query(self, msg):
        query_id, chat_ID, query_data= telepot.glance(msg, flavor='callback_query')
        message_id_tuple=telepot.origin_identifier(msg)

        #check in the db user with the current chatID
        user=next((item for item in self.users_data['users'] if item["chat_ID"] == chat_ID), False) 
        #if first time this chat_ID is used a new user is created
        if user==False:
            print("New user!")
            user=self.create_new_user(chat_ID)
            self.users_data['users'].append(user)

        if query_data=='login':
            self.bot.sendMessage(chat_ID, ('Type your User ID: '), reply_markup=self.back_login)
            user['flags']['userID_flag']=1

        elif query_data=='back_login':
            self.bot.editMessageReplyMarkup(message_id_tuple, reply_markup=None)
            self.bot.deleteMessage(message_id_tuple)
            self.bot.sendMessage(chat_ID, 'Select an option:', reply_markup=self.login_keyboard)

        elif query_data=='set':
            self.bot.sendMessage(chat_ID, 'Select an option:', reply_markup=self.settings_keyboard)
            #self.bot.sendMessage(chat_ID, 'or go back', reply_markup=back_button)

        elif query_data=='home':
            self.bot.answerCallbackQuery(query_id, text='Home')
            self.bot.editMessageReplyMarkup(message_id_tuple, reply_markup=None)
            self.bot.deleteMessage(message_id_tuple)
            self.bot.sendMessage(chat_ID, emoji.emojize(f':seedling:\tWelcome to Leaf!\t:seedling:\nYou are logged in as {user["user_ID"]}', use_aliases=True))
            self.bot.sendMessage(chat_ID, 'Select an option:', reply_markup=self.home_keyboard)

        elif query_data=='set_loc':
            self.bot.sendMessage(chat_ID, 'Chose how to set your location', reply_markup=self.location_opt_keyboard)

        elif query_data=='back':
            self.bot.answerCallbackQuery(query_id, text='Back')
            self.bot.editMessageReplyMarkup(message_id_tuple, reply_markup=None)
            self.bot.deleteMessage(message_id_tuple)

        elif query_data=='act':
            self.bot.answerCallbackQuery(query_id, text='Current Conditions')
            self.bot.sendMessage(chat_ID, 'Do you want the internal or the external conditions?', reply_markup=self.actual_menu)

        elif query_data=='tips':
            self.bot.answerCallbackQuery(query_id, text='Tips')
            tipsURL=requests.get(self.serviceURL+'/tips_catalog').json()['url']
            tip=requests.get(tipsURL+'/tip').text
            self.bot.sendMessage(chat_ID, tip , reply_markup=self.other_tip_keyboard)

        elif query_data=='send_loc':
            self.bot.sendMessage(chat_ID, 'Push the button to share your location', reply_markup=self.location_keyboard)

        elif query_data=='insert_city':
            self.bot.sendMessage(chat_ID, 'Type on your keyboard the city name:')
            user['flags']['insert_city_flag']=1

        elif query_data=='act_ext':
            adaptorURL=requests.get(self.serviceURL+'/database_adaptor').json()['url']
            if user['room_ID']==None:
                profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
                generic_room=requests.get(profileURL+'/'+user['platform_ID']+'/rooms').json()[0]['room_ID']
            else:
                generic_room=user['room_ID']
            try:
                station=str(requests.get(adaptorURL+'/'+user['platform_ID']+'/'+generic_room+'/station').json())
                station_str=f"Selected station name: {station}\n"
            except:
                station_str=''
            self.bot.answerCallbackQuery(query_id, text='Current External Conditions')
            ext_data=self.get_external_conditions(chat_ID)
            if type(ext_data['aqi'])==str:
                index=6
            elif ext_data['aqi']<=50:
                index=0
            elif ext_data['aqi']>50 and ext_data['aqi']<=100:
                index=1
            elif ext_data['aqi']>100 and ext_data['aqi']<=150:
                index=2
            elif ext_data['aqi']>150 and ext_data['aqi']<=200:
                index=3
            elif ext_data['aqi']>200 and ext_data['aqi']<=300:
                index=4
            elif ext_data['aqi']>300:
                index=5
            self.bot.sendMessage(chat_ID, emoji.emojize ("External conditions:\n"
                                                             f"{station_str}"
                                                             f"Time: {ext_data['date']}, {ext_data['time']}\n"
                                                             f"{self.aqi_state_dict[index]['circle']} AQI: {ext_data['aqi']} {self.aqi_state_dict[index]['status']}\n"
                                                        f":thermometer:\tTemperature: {ext_data['temp']}°C\n"
                                                        f":droplet:\tHumidity: {ext_data['humidity']}%\n"
                                                        f":wind_face:\tWind: {ext_data['wind']}m/s\n"
                                                        f":sunny:\tApparent temperature: {ext_data['app_temp']:.1f}°C\n"
                                                        f":cyclone:\tpm2.5 concentration: {ext_data['pm25']}\n"
                                                        f":diamond_shape_with_a_dot_inside:\tpm10 concentration: {ext_data['pm10']}\n"
                                                        ,use_aliases=True),
                                reply_markup=self.back_or_home)

        elif query_data=='other_tips':
            self.bot.answerCallbackQuery(query_id, text='Tips')
            self.bot.editMessageReplyMarkup(message_id_tuple, reply_markup=None)
            self.bot.deleteMessage(message_id_tuple)
            tipsURL=requests.get(self.serviceURL+'/tips_catalog').json()['url']
            tip=requests.get(tipsURL+'/tip').text
            self.bot.sendMessage(chat_ID, tip, reply_markup=self.other_tip_keyboard)

        elif query_data=='set_dev':
            self.bot.answerCallbackQuery(query_id, text='Device setting')
            self.bot.sendMessage(chat_ID, 'Select an option:', reply_markup=self.device_setting)

        elif query_data=='change_platform_name':
            self.bot.sendMessage(chat_ID, f'Type the new platform name for {user["platform_ID"]}:', reply_markup=self.back_button)
            user['flags']['platform_name_flag']=1

        elif query_data=='info_dev':
            output=self.get_general_info(chat_ID)
            self.bot.sendMessage(chat_ID, emoji.emojize(f"{output}", use_aliases=True), reply_markup=self.back_button)


        elif query_data=='add_room':
            self.bot.sendMessage(chat_ID, 'Type the name of the new room: ', reply_markup=self.back_button)
            user['flags']['new_room_flag']=1

        elif query_data=='remove_room':
            rooms_keyboard=self.create_rooms_keyboard(chat_ID)
            self.bot.sendMessage(chat_ID, 'Select the room you want to delete:', reply_markup=rooms_keyboard)
            user['flags']['remove_room_flag']=1

        elif query_data=='room':
            self.bot.answerCallbackQuery(query_id, text='Room menu')
            rooms_keyboard=self.create_rooms_keyboard(chat_ID)
            self.bot.sendMessage(chat_ID, f'Select the room you want to enter in:', reply_markup=rooms_keyboard)

        elif query_data=='room_set':
            self.bot.sendMessage(chat_ID, 'Select an option:', reply_markup=self.room_set_keyboard)

        elif query_data=='change_room_name':
            self.bot.sendMessage(chat_ID, f'Type the new name for the current room', reply_markup=self.back_button)
            user['flags']['room_name_flag']=1

        elif query_data=='change_thresholds':
            parameters_keyboard=self.create_parameters_keyboard(chat_ID)
            self.bot.sendMessage(chat_ID, f'Select the parameter for which you want to change the threshold', reply_markup=parameters_keyboard)

        elif query_data=='room_act':
            output=self.get_room_measures(chat_ID, user['room_ID'])
            self.bot.sendMessage(chat_ID, text=(emoji.emojize(output)), reply_markup=self.back_button)

        elif query_data=='act_int':
            output=self.get_home_measures(chat_ID)
            self.bot.sendMessage(chat_ID, text=(emoji.emojize(output)), reply_markup=self.back_button)
        
        elif query_data=='new_platform':
            self.bot.sendMessage(chat_ID, 'Write the unique platform_ID associated to your new platform')
            user['flags']['new_platform_flag']=1

        elif query_data=='stat':
            grafanaURL=requests.get(self.serviceURL+'/grafana_catalog').json()['url']
            r=requests.get(grafanaURL+"/"+user['platform_ID']+"/"+user["room_ID"]+"/dashboardURL")
            if r.status_code==200:
                dashboard_url=r.text
                period_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':chart_with_upwards_trend:Dashboard', use_aliases=True), url=dashboard_url)],
                [InlineKeyboardButton(text=emoji.emojize(':date:DAY statistics', use_aliases=True), callback_data='day')],
                [InlineKeyboardButton(text=emoji.emojize(':calendar: WEEK statistics', use_aliases=True), callback_data='week')],
                [InlineKeyboardButton(text=emoji.emojize(':spiral_calendar: MONTH statistics', use_aliases=True), callback_data='month')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])
                self.bot.sendMessage(chat_ID, 'Choose your analysis:', reply_markup=period_keyboard)
            else:
                self.bot.sendMessage(chat_ID, f"{r.reason}")
            
            

        elif query_data=='day' or query_data=='week' or query_data=='month':
            out=self.get_statistics(chat_ID, query_data)
            self.bot.sendMessage(chat_ID, text=(emoji.emojize(out)), reply_markup=self.back_button)

        elif query_data=='remove_platform':
            platforms_list=requests.get(self.clientURL+'/platforms_list'+'?username='+user['user_ID']).json()
            plt_list_keyboard=[]
            for i in platforms_list:
                emo=':small_blue_diamond:'
                plt_list_keyboard=plt_list_keyboard+[[InlineKeyboardButton(text=emoji.emojize(f'{emo}\t{i}', use_aliases=True), callback_data=i)]]
            rlk=InlineKeyboardMarkup(inline_keyboard=plt_list_keyboard)
            self.bot.sendMessage(chat_ID, text=(emoji.emojize("Select the platform you want to delete")), reply_markup=rlk)
            user['flags']['remove_platform_flag']=1
        
        elif query_data=='active_platform':
            platforms_list=requests.get(self.clientURL+'/platforms_list'+'?username='+user['user_ID']).json()
            plt_list_keyboard=[]
            emo=':small_blue_diamond:'
            for i in platforms_list:
                try:
                    platform_name=self.get_platform_name(chat_ID, i)
                except:
                    platform_name=i
                plt_list_keyboard=plt_list_keyboard+[[InlineKeyboardButton(text=emoji.emojize(f'{emo}\t{i}\t({platform_name})', use_aliases=True), callback_data=i)]]
            rlk=InlineKeyboardMarkup(inline_keyboard=plt_list_keyboard)
            self.bot.sendMessage(chat_ID, text=(emoji.emojize("Select the platform you want to visualize")), reply_markup=rlk)
            
            

        else:
            profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
            #when user clicks on a room
            try:
                rooms_info=requests.get(profileURL+'/'+user['platform_ID']+'/rooms').json()
                for room in rooms_info:
                    if query_data==room['preferences']['room_name']:
                        #when user want to remove room
                        if user['flags']['remove_room_flag']==1:
                            log=requests.delete(profileURL+'/removeRoom/'+user['user_ID']+'/'+user['platform_ID']+'/'+room['room_ID']).json()
                            if log:
                                self.bot.sendMessage(chat_ID, f"Room {room['preferences']['room_name']} succesfully removed!", reply_markup=self.home_keyboard)
                            else:
                                self.bot.sendMessage(chat_ID, f"Error while removing room {room['preferences']['room_name']}! Please try again.", reply_markup=self.home_keyboard)
                            user['flags']['remove_room_flag']=0
                        #when user want to enter a room
                        else:
                            if room['connection_flag']==1:
                                user['room_ID']=room['room_ID']
                                self.bot.sendMessage(chat_ID, f'You are now visualizing Room: {room["preferences"]["room_name"]}', reply_markup=self.room_menu)
                            else:
                                self.bot.sendMessage(chat_ID, f'Room: {room["preferences"]["room_name"]} has not been associated yet!', reply_markup=self.home_keyboard)
                    else:
                        pass
            except:
                pass
            #when user clicks a parameter
            try:
                room_info=requests.get(profileURL+'/'+user['platform_ID']+'/rooms/'+user['room_ID']).json()
                for parameter in room_info['preferences']['thresholds'].keys():
                    if query_data==parameter:
                        th_current=self.get_thresholds(chat_ID, user['room_ID'],parameter, False)
                        th_optimal=self.get_thresholds(chat_ID, user['room_ID'],parameter, True)
                        self.bot.sendMessage(chat_ID, f"The current thresholds for {parameter} are: {th_current['min']} {th_current['max']}")
                        self.bot.sendMessage(chat_ID, f"The optimal thresholds for {parameter} are: {th_optimal['min']} {th_optimal['max']}")
                        self.bot.sendMessage(chat_ID, 'Type the new threshold values as min and max value separated by a space')
                        self.thresholds.append({"chat_ID":chat_ID,"parameter":parameter})
                        user['flags']['thresholds_flag']=1
            except Exception as e:
                print(e)
                pass

            try:
                #when user clicks on a platform
                platforms_list=requests.get(self.clientURL+'/platforms_list'+'?username='+user['user_ID']).json()
                for i in platforms_list:
                    if query_data==i:
                        #when user wants to delete a platform
                        if user['flags']['remove_platform_flag']==1:
                            log=requests.delete(profileURL+'/removeProfile/'+user["user_ID"]+'/'+user["platform_ID"])
                            if log.status_code==200:
                                self.bot.sendMessage(chat_ID, f"Platform {i} succesfully removed!")
                                keyboard=self.create_platforms_keyboard(chat_ID)
                                self.bot.sendMessage(chat_ID, 'Choose the registered platform you want to visualize or register a new one', reply_markup=keyboard)
                            else:
                                self.bot.sendMessage(chat_ID, f"{log.reason} Please try again.", reply_markup=self.home_keyboard)
                            user['flags']['remove_platform_flag']=0
                        else:
                            user['platform_ID']=i
                            self.users_data['users']=[user if x['chat_ID']==chat_ID else x for x in self.users_data['users']]
                            profileURL=requests.get(self.serviceURL+'/profiles_catalog').json()['url']
                            platform_name=requests.get(profileURL+'/'+user['platform_ID']+'/platform_name').json()
                            self.bot.sendMessage(chat_ID, f'You are now visualizing Platform: {user["platform_ID"]} ({platform_name})')
                            self.bot.sendMessage(chat_ID, 'Before starting, go to Settings to set your position and configure your device or go to the main menu', reply_markup=self.starting_keyboard)
            except:
                pass

        self.users_data['users']=[user if x['chat_ID']==chat_ID else x for x in self.users_data['users']]

    def POST(self,*uri):
        if uri[0]=='warning':
            platform_ID=uri[1]
            room_ID=uri[2]
            profileURL=self.retrieveService('profiles_catalog')['url']
            body=cherrypy.request.body.read()
            jsonBody=json.loads(body)
            status=jsonBody["status"]
            parameter=jsonBody["parameter"]
            platform=requests.get(profileURL+"/"+platform_ID+"/platform_name").json()
            room=requests.get(profileURL+"/"+platform_ID+"/rooms/"+room_ID+"/preferences/room_name").json()
            tip=jsonBody["tip"]
            if status!="OK":
                tosend=":warning:WARNING!!!\n{} is {} in {} - {}".format(parameter,status,room,platform)
            else:
                tosend=":confetti_ball:Good news!!!\n{} is {} again in {} - {}".format(parameter,status,room,platform)
            if tip!=None:
                tosend+=f'\nTip: {tip}'
            chat_IDs=requests.get(self.clientURL+"/info/"+platform_ID+"/chatIDs").json()
            chat_IDs = list(dict.fromkeys(chat_IDs))
            for chat_ID in chat_IDs:
                try:
                    self.bot.sendMessage(chat_ID, text=emoji.emojize(tosend), reply_markup=self.back_button)
                except:
                    pass


if __name__ == "__main__":
    conf=sys.argv[1]
    conf_content=json.load(open(conf,"r"))
    bot=LeafBot(conf)
    print(conf)

    if bot.service is not False:
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
            }
        }
        cherrypy.tree.mount(bot, bot.service, conf)
        cherrypy.config.update({'server.socket_host': conf_content['IP_address']})
        cherrypy.config.update({'server.socket_port': conf_content['IP_port']})
        cherrypy.engine.start()
        cherrypy.engine.block()

    while 1:
        pass
    
