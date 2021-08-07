#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 12:12:24 2020

@author: tommasocarluccio
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 09:43:24 2020

@author: tommasocarluccio
"""

import telepot
import requests
import numpy as np
import time
import emoji
import random
import json
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


#https://api.telegram.org/bot1149502005:AAEfKVLPHZ98DvzpiG8ltYWBOMKn5PvVbZk/
class bot_Class(object):

    def __init__(self):
        self.bot=telepot.Bot('1149502005:AAEfKVLPHZ98DvzpiG8ltYWBOMKn5PvVbZk')
        self.api_create()
        self.restart=0
        
    def api_create(self, latitude=41.9109, longitude=12.4818):
        self.latitude=latitude
        self.longitude=longitude
        #api_url=('http://api.waqi.info/feed/geo:45.059404;7.641922/?token=8b03b422d0b7122fefecf85cf73b81eddcd7a589')
        self.api_url=('http://api.waqi.info/feed/geo:'+str(self.latitude)+';'+str(self.longitude)+'/?token=8b03b422d0b7122fefecf85cf73b81eddcd7a589')
        self.api_data=requests.get(self.api_url).json()
        #print(self.api_data)
        self.e_aqi=self.api_data['data']['aqi']
        self.station=self.api_data['data']['city']['name']
        self.idx_station=self.api_data['data']['idx']
        self.e_timestamp=self.api_data['data']['time']['s']
        self.e_date=self.e_timestamp.split(' ')[0]
        self.e_time=self.e_timestamp.split(' ')[1]
        try:
            self.e_pm25=self.api_data['data']['iaqi']['pm25']['v']
        except:
            self.e_pm25='-Unavailable-'
        try:
            self.e_pm10=self.api_data['data']['iaqi']['pm10']['v']
        except:
            self.e_pm10='-Unavailable-'
        self.e_temp=self.api_data['data']['iaqi']['t']['v']
        self.e_humidity=self.api_data['data']['iaqi']['h']['v']
        self.vap_pres=(self.e_humidity/100)*6.105*np.exp(17.27*((self.e_temp)/(237+self.e_temp)))
        try:
            self.e_wind=self.api_data['data']['iaqi']['w']['v']
            self.e_app_temp=self.e_temp+0.33*(self.vap_pres)-(0.7*self.e_wind)-4
        except:
            self.e_wind='-Unavailable-'
            self.e_app_temp=self.e_temp+0.33*(self.vap_pres)-4

    def api_create2(self, new_city='Milan'):
        self.new_city=new_city
        self.api_url=('http://api.waqi.info/feed/'+self.new_city+'/?token=8b03b422d0b7122fefecf85cf73b81eddcd7a589')
        try:
            self.api_data=requests.get(self.api_url).json()
            self.e_aqi=self.api_data['data']['aqi']
            self.station=self.api_data['data']['city']['name']
            self.idx_station=self.api_data['data']['idx']
            self.e_timestamp=self.api_data['data']['time']['s']
            self.e_date=self.e_timestamp.split(' ')[0]
            self.e_time=self.e_timestamp.split(' ')[1]
            try:
                self.e_pm25=self.api_data['data']['iaqi']['pm25']['v']
            except:
                self.e_pm25='-Unavailable-'
            try:
               self.e_pm10=self.api_data['data']['iaqi']['pm10']['v']
            except:
                self.e_pm10='-Unavailable-'
            self.e_temp=self.api_data['data']['iaqi']['t']['v']
            self.e_humidity=self.api_data['data']['iaqi']['h']['v']
            self.vap_pres=(self.e_humidity/100)*6.105*np.exp(17.27*((self.e_temp)/(237+self.e_temp)))
            try:
                self.e_wind=self.api_data['data']['iaqi']['w']['v']
                self.e_app_temp=self.e_temp+0.33*(self.vap_pres)-(0.7*self.e_wind)-4
            except:
                self.e_wind='-Unavailable-'
                self.e_app_temp=self.e_temp+0.33*(self.vap_pres)-4
            self.city_status=11
        except:
            self.bot.sendMessage(self.chat_id, 'Invalid city name!')
            self.city_status=0

    def on_chat_message(self, msg):
        content_type, chat_type, self.chat_id = telepot.glance(msg)
        user_name = msg['from']['first_name']

        starting_keyboard= InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':gear: Settings', use_aliases=True), callback_data='set')],
                [InlineKeyboardButton(text=emoji.emojize(':house: Go to the main menu', use_aliases=True), callback_data= 'home')],
                ])

        if content_type=='text' and self.status==11:
            new_city=msg['text']
            self.api_create2(new_city)
            if self.city_status==11:
                self.bot.sendMessage(self.chat_id, 'Your location has been succesfully updated!')
                self.bot.sendMessage(self.chat_id, f'The nearest active station to the inserted city found is: {self.station}')
                self.bot.sendMessage(self.chat_id, 'Select an option:', reply_markup=self.home_keyboard)
                print('New station:'+self.station)
                self.status=0
            else:
                self.bot.sendMessage(self.chat_id, 'Select an option:', reply_markup=self.home_keyboard)
                self.status=0

        elif content_type=='text' and self.userID_flag==1 and self.password_flag==0:
            self.userID=msg['text']
            print(self.userID)
            users_file= open('registration/reg.json',"r")
            users_dict=json.loads(users_file.read())
            IP_file=open('ID_IP.json', "r")
            IP_dict=json.loads(IP_file.read())
            print(IP_dict)
            user=0
            while user<len(users_dict) and self.userID_flag==1:
                if users_dict[user]['user_ID']==self.userID:
                    self.password=users_dict[user]['password']
                    self.catalogID=users_dict[user]['catalog_id']
                    print(self.catalogID)
                    IP=0
                    while IP<len(IP_dict):
                        if IP_dict[IP]['catalogID']==self.catalogID:
                            self.catalogIP=IP_dict[IP]['catalogIP']
                            print(self.catalogIP)
                            break
                    self.userID_flag=0
                    self.password_flag=1
                    self.bot.sendMessage(self.chat_id, f'Now type your password for {self.userID}:', reply_markup=self.back_login)
                else:
                    user=user+1
            if user==len(users_dict) and self.userID_flag==1:
                self.bot.sendMessage(self.chat_id, f'User ID "{self.userID}" not found\nTry another User ID:', reply_markup=self.back_login)

        elif content_type=='text' and self.userID_flag==0 and self.password_flag==1:
            if msg['text']==self.password:
                self.bot.sendMessage(self.chat_id, emoji.emojize(f':seedling:\tHello {user_name} Welcome to Leaf!\t:seedling:\nYou are logged in as {self.userID}', use_aliases=True))
                self.bot.sendMessage(self.chat_id, 'Before starting, go to Settings to set your position and configure your device or go to the main menu', reply_markup=starting_keyboard)
                self.logged=1
                self.restart=1
                self.password_flag=0
                self.userID_flag=0
                self.flag_t=0
                self.flag_a=0
                self.flag_h=0
                self.chat_catalog.append({self.chat_id:self.catalogID})
                with open('chat_catalog.json', 'w') as outfile:
                    json.dump(self.chat_catalog, outfile)
                
                
            else:
                self.bot.sendMessage(self.chat_id, f'Wrong password for {self.userID}\n Try again:', reply_markup=self.back_login)

        elif content_type=='text' and self.room_flag==1:
            roomID=self.name_id_dic[self.entered_room]
            new_name=msg['text'] #clientID=room
            x={"roomID":roomID, "newRoomName":new_name}
            requests.put(bot_c.catalogue_url+'/changeRoomName', data=json.dumps(x))
            #put to catalog
            self.bot.sendMessage(self.chat_id, f'Room name successfully updated!\nNew room name: {new_name}\nSelect an option:', reply_markup=self.room_menu)
            self.room_flag=0

        elif content_type=='text' and self.user_flag==1:
            self.userID=msg['text']
            x={"newClientID":self.userID}
            requests.put(bot_c.catalogue_url+'/changeClientID', data=json.dumps(x))
            #put to catalog
            self.bot.sendMessage(self.chat_id, f'User name successfully updated!\nNew user name: {self.userID}\nSelect an option:', reply_markup=self.home_keyboard)
            self.user_flag=0


        elif content_type=='text' and self.new_room_flag==1:
            room_name=msg['text']
            params={"roomID":room_name}
            requests.put(self.catalogue_url+'/insertRoom', json=params)
            self.bot.sendMessage(self.chat_id, f'Room "{room_name}" added!\nSelect an option', reply_markup=self.home_keyboard)
            self.new_room_flag=0

        elif content_type=='text' and self.status==0 and self.room_flag==0 and self.user_flag==0:
            txt = msg['text']
            if txt=='/start':
                self.bot.sendMessage(self.chat_id, emoji.emojize(':seedling:\t Welcome to Leaf!\t:seedling:\nBefore starting Log into your Leaf account or create one', use_aliases=True), reply_markup=self.login_keyboard)
            elif txt=='/help':
                self.bot.sendMessage(self.chat_id, emoji.emojize(':black_circle:\tPress /start to start the bot and open the Home menu\n'
                                     ':black_circle:\tUse the displayed keyboard to navigate through the bot functions\n'
                                     ':black_circle:\tUse the "Set your Location" button to change the previously registered location and access the data of the nearest available station through the "Actual Condition" menù\n'
                                     ,use_aliases=True), reply_markup=self.back_button)
            else:
                self.bot.sendMessage(self.chat_id ,'Invalid command!\n'
                                     'To restart the bot use : /start\n'
                                     'To get help use: /help')

        elif content_type=='location':
            user_location=msg['location']
            latitude=user_location['latitude']
            longitude=user_location['longitude']
            self.api_create(latitude, longitude)
            self.bot.sendMessage(self.chat_id, 'Your location has been Succesfully updated!', reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            self.bot.sendMessage(self.chat_id, f'The nearest active station found is: {self.station}')
            self.bot.sendMessage(self.chat_id, 'Select an option:', reply_markup=self.home_keyboard)
            print('New nearest station found: '+self.station)

        else:
            self.bot.sendMessage(self.chat_id ,'Invalid command!\n'
                                 'To restart the bot use : /start\n'
                                 'To get help use: /help')


    def on_callback_query(self, msg):
        query_id, self.chat_id, query_data= telepot.glance(msg, flavor='callback_query')
        message_id_tuple=telepot.origin_identifier(msg)
        
        
        room_list_keyboard=[]
        for i in self.rooms_list:
            j=self.id_name_dic[i]
            try:
                emo=self.emoji_dic[j]
            except:
                emo=':small_blue_diamond:'
            room_list_keyboard=room_list_keyboard+[[InlineKeyboardButton(text=emoji.emojize(f'{emo}\t{j}', use_aliases=True), callback_data=j)]] 
        room_list_keyboard=room_list_keyboard+[[InlineKeyboardButton(text=emoji.emojize(':back:\tBACK', use_aliases=True), callback_data='back')]] 
        rlk=InlineKeyboardMarkup(inline_keyboard=room_list_keyboard)
        '''
        starting_keyboard= InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':gear: Settings', use_aliases=True), callback_data='set')],
                [InlineKeyboardButton(text=emoji.emojize(':house: Go to the main menu', use_aliases=True), callback_data= 'home')],
                ])
        '''
        actual_menu=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= emoji.emojize(':house: Internal Conditions', use_aliases=True), callback_data='act_int'),
                InlineKeyboardButton(text= emoji.emojize(':earth_africa: External Conditions', use_aliases=True), callback_data='act_ext')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

        settings_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= emoji.emojize(':globe_with_meridians: Location settings', use_aliases=True), callback_data='set_loc'),
                InlineKeyboardButton(text= emoji.emojize(':computer: System settings', use_aliases=True), callback_data='set_dev')],
                [InlineKeyboardButton(text= emoji.emojize(':question: Get info on your device', use_aliases=True), callback_data='info_dev')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

        device_setting=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= emoji.emojize(':house: Add a new room', use_aliases=True), callback_data='add_room'),
                InlineKeyboardButton(text= emoji.emojize(':heavy_multiplication_x: Remove a room', use_aliases=True), callback_data='remove_room')],
                [InlineKeyboardButton(text= emoji.emojize(':pencil2: Change user name', use_aliases=True), callback_data='change_user_name')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

        #stat_menu=InlineKeyboardMarkup(inline_keyboard=[
                #[InlineKeyboardButton(text= emoji.emojize(':globe_with_meridians: AQI', use_aliases=True), callback_data='aqi'),
                 #InlineKeyboardButton(text= emoji.emojize(':thermometer: Temperature', use_aliases=True), callback_data='temp')],
                 #[InlineKeyboardButton(text= emoji.emojize(':droplet: Humidity', use_aliases=True), callback_data='hum'),
                 #InlineKeyboardButton(text= emoji.emojize(':hot_face: Apparent Temperature', use_aliases=True), callback_data='app_temp')],
                 #[InlineKeyboardButton(text= emoji.emojize(':dash: GAS', use_aliases=True), callback_data='gas')],
                 #[InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                 #])

        time_menu=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= emoji.emojize(':date: DAY statistics', use_aliases=True), callback_data='day')],
                [InlineKeyboardButton(text= emoji.emojize(':calendar: WEEK statistics', use_aliases=True), callback_data='week')],
                [InlineKeyboardButton(text= emoji.emojize(':spiral_calendar: MONTH statistics', use_aliases=True), callback_data='month')],
                [InlineKeyboardButton(text= emoji.emojize(':watch: REAL TIME statistics', use_aliases=True), callback_data='real_time')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

        back_or_home=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')],
                [InlineKeyboardButton(text=emoji.emojize(':house: Go to the main menu', use_aliases=True), callback_data= 'home')],
                ])

        location_keyboard=ReplyKeyboardMarkup(keyboard=[
                [KeyboardButton(text='Send your location', request_location=True)]
                ])

        location_opt_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':round_pushpin:\tSend your current position', use_aliases=True), callback_data='send_loc')],
                [InlineKeyboardButton(text=emoji.emojize(':cityscape:\tInsert City', use_aliases=True), callback_data='insert_city')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])


        day_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':green_circle:Day Statistics:green_circle:', use_aliases=True), url='192.168.1.130:8091/day')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

        week_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=emoji.emojize(':green_circle:Week Statistics:green_circle:', use_aliases=True), url='192.168.1.130:8091/week')],
                    [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                    ])

        month_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=emoji.emojize(':green_circle:Month Statistics:green_circle:', use_aliases=True), url='192.168.1.130:8091/month')],
                    [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                    ])

        rt_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':green_circle:Real Time Statistics:green_circle:', use_aliases=True), url='192.168.1.130:8091/actual')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

        other_tip_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':pencil: Another Tip!', use_aliases=True), callback_data='other_tips'),
                InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

        self.room_set_keyboard=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':pencil2: Change room name', use_aliases=True), callback_data='change_room_name'),
                 InlineKeyboardButton(text=emoji.emojize(':heavy_multiplication_x: Delete sensor', use_aliases=True), callback_data='delete_sensor')],
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])


        #double_back_button=InlineKeyboardMarkup(inline_keyboard=[
                #[InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='2back')]
                #])
        #empty_keyboard=InlineKeyboardMarkup(inline_keyboard=[])


        if query_data=='login':
            self.bot.sendMessage(self.chat_id, ('Type your User ID: '), reply_markup=self.back_login)
            self.userID_flag=1

        if query_data=='act':
            self.bot.answerCallbackQuery(query_id, text='Actual Conditions')
            self.bot.sendMessage(self.chat_id, 'Do you want the internal or the external conditions?', reply_markup=actual_menu)

        if query_data=='stat':
            self.bot.answerCallbackQuery(query_id, text='Statistics')
            self.bot.sendMessage(self.chat_id, 'Choose the period of time for your statistic:', reply_markup=time_menu)

        if query_data=='home':
            self.bot.answerCallbackQuery(query_id, text='Home')
            self.bot.editMessageReplyMarkup(message_id_tuple, reply_markup=None)
            self.bot.deleteMessage(message_id_tuple)
            self.bot.sendMessage(self.chat_id, 'Select an option:', reply_markup=self.home_keyboard)
            self.room_flag=0
            self.user_flag=0
            self.userID_flag=0
            self.password_flag=0
            self.new_sensor_flag=0
            self.new_room_flag=0
            self.enter_room_flag==0

        if query_data=='back_login':
            self.bot.editMessageReplyMarkup(message_id_tuple, reply_markup=None)
            self.bot.deleteMessage(message_id_tuple)
            self.bot.sendMessage(self.chat_id, 'Select an option:', reply_markup=self.login_keyboard)
            self.room_flag=0
            self.user_flag=0
            self.userID_flag=0
            self.password_flag=0
            self.new_sensor_flag=0
            self.new_room_flag=0
            self.enter_room_flag==0

        if query_data=='room':
            self.bot.answerCallbackQuery(query_id, text='Room menu')
            self.bot.sendMessage(self.chat_id, f'Select the room you want to enter in:', reply_markup=rlk)
            self.enter_room_flag=1

        if query_data=='room_act':
            self.bot.sendMessage(self.chat_id, emoji.emojize(f'{self.room_strin}', use_aliases=True), reply_markup=back_or_home)

        if query_data=='room_set':
            self.bot.sendMessage(self.chat_id, 'Select an option:', reply_markup=self.room_set_keyboard)
            
        if query_data=='remove_room':
            self.bot.sendMessage(self.chat_id, 'Select the room you want to delete:', reply_markup=rlk)
            self.delete_room_flag=1

        if query_data=='set_dev':
            self.bot.answerCallbackQuery(query_id, text='Device setting')
            self.bot.sendMessage(self.chat_id, 'Select an option:', reply_markup=device_setting)

        if query_data=='add_room':
            self.bot.sendMessage(self.chat_id, 'Type the name of the new room: ', reply_markup=self.back_button)
            self.new_room_flag=1

        if query_data=='set':
            self.bot.sendMessage(self.chat_id, 'Select an option:', reply_markup=settings_keyboard)
            #self.bot.sendMessage(self.chat_id, 'or go back', reply_markup=back_button)

        if query_data=='set_loc':
            self.bot.sendMessage(self.chat_id, 'Chose how to set your location', reply_markup=location_opt_keyboard)
            #self.bot.sendMessage(self.chat_id, 'or go back', reply_markup=back_button)

        if query_data=='send_loc':
            self.bot.sendMessage(self.chat_id, 'Push the button to share your location', reply_markup=location_keyboard)

        if query_data=='insert_city':
            self.bot.sendMessage(self.chat_id, 'Type on your keyboard the city name:')
            self.status=11
        #if query_data=='day' or query_data=='week' or query_data=='month':
        #    self.bot.sendMessage(chat_id, 'Chose the interval of time for your statistics', reply_markup=stat_menu)

        #clientID=room
        if query_data=='change_room_name':
            self.bot.sendMessage(self.chat_id, f'Type the new name for {self.entered_room}', reply_markup=self.back_button)
            self.room_flag=1

        if query_data=='change_user_name':
            self.bot.sendMessage(self.chat_id, 'Type the new user name:', reply_markup=self.back_button)
            self.user_flag=1

        if query_data=='delete_sensor':
            self.bot.sendMessage(self.chat_id, f'Select the sensor you want to delete', reply_markup=self.dlk)
           #something

        if query_data=='info_dev':
            #print(self.strin_info)
            self.bot.sendMessage(self.chat_id, emoji.emojize(f"{self.strin_info}", use_aliases=True), reply_markup=self.back_button)

        if query_data=='back':
            self.bot.answerCallbackQuery(query_id, text='Back')
            self.bot.editMessageReplyMarkup(message_id_tuple, reply_markup=None)
            self.bot.deleteMessage(message_id_tuple)

        if query_data=='tips':
            self.bot.answerCallbackQuery(query_id, text='Tips')
            self.bot.sendMessage(self.chat_id, random.choice(lines), reply_markup=other_tip_keyboard)

        if query_data=='other_tips':
            self.bot.answerCallbackQuery(query_id, text='Tips')
            self.bot.editMessageReplyMarkup(message_id_tuple, reply_markup=None)
            self.bot.deleteMessage(message_id_tuple)
            self.bot.sendMessage(self.chat_id, random.choice(lines), reply_markup=other_tip_keyboard)

        if query_data=='act_int':
            self.get_info_flag=1
            self.bot.sendMessage(self.chat_id, emoji.emojize(f"{self.strin}", use_aliases=True),reply_markup=back_or_home)


        if query_data=='act_ext':
            self.bot.answerCallbackQuery(query_id, text='Actual External Conditions')
            if self.e_aqi<=50:
                self.bot.sendMessage(self.chat_id, emoji.emojize ("External conditions:\n"
                                                             f"Selected station name: {self.station}\n"
                                                             f"Time: {self.e_date}, {self.e_time}\n"
                                                             f":green_circle: AQI: {self.e_aqi} GOOD\n"
                                                        f":thermometer:\tTemperature: {self.e_temp}°C\n"
                                                        f":droplet:\tHumidity: {self.e_humidity}%\n"
                                                        f":wind_face:\tWind: {self.e_wind}m/s\n"
                                                        f":sunny:\tApparent temperature: {self.e_app_temp:.1f}°C\n"
                                                        f":cyclone:\tpm2.5 concentration: {self.e_pm25}\n"
                                                        f":diamond_shape_with_a_dot_inside:\tpm10 concentration: {self.e_pm10}\n"
                                                        ,use_aliases=True),
                                reply_markup=back_or_home)
            elif self.e_aqi>50 and self.e_aqi<=100:
                self.bot.sendMessage(self.chat_id, emoji.emojize ("External conditions:\n"
                                                             f"Selected station name: {self.station}\n"
                                                             f"Time: {self.e_date}, {self.e_time}\n"
                                                             f":yellow_circle: AQI: {self.e_aqi} MODERATE\n"
                                                        f":thermometer:\tTemperature: {self.e_temp}°C\n"
                                                        f":droplet:\tHumidity: {self.e_humidity}%\n"
                                                        f":wind_face:\tWind: {self.e_wind}m/s\n"
                                                        f":sunny:\tApparent temperature: {self.e_app_temp:.1f}°C\n"
                                                        f":cyclone:\tpm2.5 concentration: {self.e_pm25}\n"
                                                        f":diamond_shape_with_a_dot_inside:\tpm10 concentration: {self.e_pm10}\n"
                                                        ,use_aliases=True),
                                reply_markup=back_or_home)
            elif self.e_aqi>100 and self.e_aqi<=150:
                self.bot.sendMessage(self.chat_id, emoji.emojize ("External conditions:\n"
                                                             f"Selected station name: {self.station}\n"
                                                             f"Time: {self.e_date}, {self.e_time}\n"
                                                             f":orange_circle: AQI: {self.e_aqi} UNHEALTHY for Sensitive Groups\n"
                                                        f":thermometer:\tTemperature: {self.e_temp}°C\n"
                                                        f":droplet:\tHumidity: {self.e_humidity}%\n"
                                                        f":wind_face:\tWind: {self.e_wind}m/s\n"
                                                        f":sunny:\tApparent temperature: {self.e_app_temp:.1f}°C\n"
                                                        f":cyclone:\tpm2.5 concentration: {self.e_pm25}\n"
                                                        f":diamond_shape_with_a_dot_inside:\tpm10 concentration: {self.e_pm10}\n"
                                                        ,use_aliases=True),
                                reply_markup=back_or_home)
            elif self.e_aqi>150 and self.e_aqi<=200:
                self.bot.sendMessage(self.chat_id, emoji.emojize ("External conditions:\n"
                                                             f"Selected station name: {self.station}\n"
                                                             f"Time: {self.e_date}, {self.e_time}\n"
                                                             f":red_circle: AQI: {self.e_aqi} UNHEALTHY\n"
                                                        f":thermometer:\tTemperature: {self.e_temp}°C\n"
                                                        f":droplet:\tHumidity: {self.e_humidity}%\n"
                                                        f":wind_face:\tWind: {self.e_wind}m/s\n"
                                                        f":sunny:\tApparent temperature: {self.e_app_temp:.1f}°C\n"
                                                        f":cyclone:\tpm2.5 concentration: {self.e_pm25}\n"
                                                        f":diamond_shape_with_a_dot_inside:\tpm10 concentration: {self.e_pm10}\n"
                                                        ,use_aliases=True),
                                reply_markup=back_or_home)
            elif self.e_aqi>200 and self.e_aqi>=300:
                self.bot.sendMessage(self.chat_id, emoji.emojize ("External conditions:\n"
                                                             f"Selected station name: {self.station}\n"
                                                             f"Time: {self.e_date}, {self.e_time}\n"
                                                             f":purple_circle: AQI: {self.e_aqi} VERY UNHEALTHY\n"
                                                        f":thermometer:\tTemperature: {self.e_temp}°C\n"
                                                        f":droplet:\tHumidity: {self.e_humidity}%\n"
                                                        f":wind_face:\tWind: {self.e_wind}m/s\n"
                                                        f":sunny:\tApparent temperature: {self.e_app_temp:.1f}°C\n"
                                                        f":cyclone:\tpm2.5 concentration: {self.e_pm25}\n"
                                                        f":diamond_shape_with_a_dot_inside:\tpm10 concentration: {self.e_pm10}\n"
                                                        ,use_aliases=True),
                                reply_markup=back_or_home)
            elif self.e_aqi>300:
                self.bot.sendMessage(self.chat_id, emoji.emojize ("External conditions:\n"
                                                             f"Selected station name: {self.station}\n"
                                                             f"Time: {self.e_date}, {self.e_time}\n"
                                                             f":brown_circle: AQI: {self.e_aqi} HAZARDOUS\n"
                                                        f":thermometer:\tTemperature: {self.e_temp}°C\n"
                                                        f":droplet:\tHumidity: {self.e_humidity}%\n"
                                                        f":wind_face:\tWind: {self.e_wind}m/s\n"
                                                        f":sunny:\tApparent temperature: {self.e_app_temp:.1f}°C\n"
                                                        f":cyclone:\tpm2.5 concentration: {self.e_pm25}\n"
                                                        f":diamond_shape_with_a_dot_inside:\tpm10 concentration: {self.e_pm10}\n"
                                                        ,use_aliases=True),
                                reply_markup=back_or_home)

        if query_data=='day':
            self.bot.sendMessage(self.chat_id, 'Press the botton to open the statistic page',reply_markup=day_keyboard)

        if query_data=='week':
            self.bot.sendMessage(self.chat_id, 'Press the botton to open the statistic page',reply_markup=week_keyboard)

        if query_data=='month':
            self.bot.sendMessage(self.chat_id, 'Press the botton to open the statistic page',reply_markup=month_keyboard)

        if query_data=='real_time':
            self.bot.sendMessage(self.chat_id, 'Press the botton to open the statistic page',reply_markup=rt_keyboard)

        for i in self.rooms_list:
            if query_data==self.id_name_dic[i] and self.enter_room_flag==1: #respond to enter a room
                self.entered_room=self.id_name_dic[i]
                self.bot.sendMessage(self.chat_id, f'Now you are in {self.entered_room}\nSelect an option:', reply_markup=self.room_menu)
                self.entered_room_flag=1
                self.enter_room_flag=0
            elif query_data==self.id_name_dic[i] and self.delete_room_flag==1: #respond to remove a room
                selected_room=self.id_name_dic[i]
                par={"room":selected_room}
                requests.delete(self.catalogue_url+'/removeRoom', params=par)
                self.bot.editMessageReplyMarkup(message_id_tuple, reply_markup=None)
                self.bot.deleteMessage(message_id_tuple)
                self.bot.sendMessage(self.chat_id, f'{selected_room} removed!\nSelect an option:', reply_markup=device_setting)
                self.delete_room_flag=0
                
        for i in self.dev_name_list:
            if query_data==i:
                selected_device=i
                par={"room":self.entered_room, "device":selected_device}
                requests.delete(self.catalogue_url+'/removeDevice', params=par)
                self.bot.editMessageReplyMarkup(message_id_tuple, reply_markup=None)
                self.bot.deleteMessage(message_id_tuple)
                self.bot.sendMessage(self.chat_id, f'{selected_device} removed!\nSelect an option:', reply_markup=self.room_set_keyboard)

    def run(self):

        self.bot.message_loop({"chat": self.on_chat_message,
                          'callback_query': self.on_callback_query})

if __name__=='__main__':
    bot_c=bot_Class()
    bot_c.run()

    bot_c.status=0
    bot_c.room_flag=0
    bot_c.user_flag=0
    bot_c.userID_flag=0
    bot_c.password_flag=0
    bot_c.new_sensor_flag=0
    bot_c.new_room_flag=0
    bot_c.enter_room_flag=0
    bot_c.entered_room_flag=0
    bot_c.delete_room_flag=0
    bot_c.sensor_list=[]
    bot_c.flag_t=1
    bot_c.flag_h=1
    bot_c.flag_a=1
    bot_c.users=[]
    bot_c.dev_name_list=[]
    bot_c.entered_room=''
    bot_c.room_strin=''
    bot_c.catalogIP=''
    bot_c.rooms_list=[]
    bot_c.logged=0



    #get url of catalog
    bot_c.chat_catalog=json.load(open('chat_catalog.json'))
    
    #catalogue=json.load(open('catalog/catalog_settings.json'))
    #IP_address=catalogue['catalog'][0]['addressIP']
   # port=catalogue['catalog'][0]['port']
    bot_c.catalogue_url='http://'+bot_c.catalogIP+'/catalog'


    bot_c.emoji_dic={
        "temperature":":thermometer:",
        "humidity":":droplet:",
        "AQI":":cyclone:",
        "Bedroom":":zzz:",
        "Kitchen":":fork_and_knife:",
        "Bathroom":":bathtub:"
        }


    find_more=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=emoji.emojize(':exclamation_question_mark: Find out more', use_aliases=True), callback_data='act_int'),
             InlineKeyboardButton(text=emoji.emojize(':back: Ignore', use_aliases=True), callback_data='back')]
            ])

    bot_c.home_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= emoji.emojize(':watch: Actual Conditions', use_aliases=True), callback_data='act'),
                InlineKeyboardButton(text= emoji.emojize(':key: Enter a Room', use_aliases=True), callback_data='room')],
                [InlineKeyboardButton(text=emoji.emojize(':green_book: Tips', use_aliases=True), callback_data='tips'),
                InlineKeyboardButton(text=emoji.emojize(':gear: Settings',use_aliases=True), callback_data='set')]
                ])
    bot_c.room_menu=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text= emoji.emojize(':bar_chart: Room statistics', use_aliases=True), callback_data='stat'),
                InlineKeyboardButton(text= emoji.emojize(':gear: Room settings', use_aliases=True), callback_data='room_set')],
                [InlineKeyboardButton(text=emoji.emojize(':watch: Room actual conditions', use_aliases=True), callback_data='room_act')],
                [InlineKeyboardButton(text=emoji.emojize(':house: Go to the main menu', use_aliases=True), callback_data='home')]
                ])

    bot_c.back_button=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back')]
                ])

    bot_c.back_login=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':back: BACK', use_aliases=True), callback_data='back_login')]
                ])

    bot_c.home_button=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':house: HOME', use_aliases=True), callback_data='home')]
                ])



    bot_c.login_keyboard= InlineKeyboardMarkup (inline_keyboard=[
                [InlineKeyboardButton(text=emoji.emojize(':gear: LOGIN', use_aliases=True), callback_data='login')],
                [InlineKeyboardButton(text=emoji.emojize(':green_circle:Register on the website:green_circle:', use_aliases=True), url='0.0.0.0:9990/reg.html')],
                ])

    with open('Tips.txt') as f:
        lines = f.readlines()

    while 1: #and bot_c.logged==1:
        if bot_c.logged==1:
            bot_c.catalogue_url='http://'+bot_c.catalogIP+'/catalog'
    
            bot_c.room_list=requests.get(bot_c.catalogue_url+'/rooms').json()
    
            bot_c.id_name_dic={}
            for ro in bot_c.room_list:
                roID=ro['roomID']
                ro_name=ro['room_name']
                new={roID:ro_name}
                bot_c.id_name_dic.update(new)
            bot_c.name_id_dic={}
            for ro in bot_c.room_list:
                roID=ro['roomID']
                ro_name=ro['room_name']
                new={ro_name:roID}
                bot_c.name_id_dic.update(new)
    
            bot_c.rooms_list=requests.get(bot_c.catalogue_url+'/roomsList').json()
            bot_c.rooms_string=''
            for i in bot_c.rooms_list:
                bot_c.rooms_string=(bot_c.rooms_string+bot_c.id_name_dic[i]+', ')
            bot_c.rooms_string=bot_c.rooms_string[:-2]
    
            bot_c.strin=''
            bot_c.strin_info=''
            user_name=requests.get(bot_c.catalogue_url+'/clientID').json()
            bot_c.strin_info=('Your Leaf device:\n:bust_in_silhouette:\tUser name: '+user_name+'\n\n')
            ##GET ACTUAL CONDITIONS FOR THE HOUSE
            for room in bot_c.room_list:
                room_ID=room['roomID']
                room_ID=bot_c.id_name_dic[room_ID]
                try:
                    last_update=room['last_update']
                except:
                    last_update='None'
                try:
                    emo_room=bot_c.emoji_dic[room_ID]
                except:
                    emo_room=':house:'
                bot_c.strin=(bot_c.strin+emo_room+'\t'+room_ID+':\n')
                bot_c.strin=(bot_c.strin+'\t:hourglass:\tLast update: '+last_update+'\n')
                bot_c.strin_info=(bot_c.strin_info+':house:\tRoom name: '+room_ID+':\n')
                bot_c.strin_info=(bot_c.strin_info+'\t:hourglass:\tLast update: '+last_update+'\n')
                hum_int='NaN'
                temp_int='NaN'
                for devices in room['devices']:
                    device=devices['sensorID']
                    bot_c.strin_info=(bot_c.strin_info+'\t:small_orange_diamond:\tSensor '+device+':\n')
                    parami=''
                    for param in devices['parameters']:
                        parameter=param['parameter']
                        #CHECK ON TEMPERATURE VALUE
                        if parameter=='temperature':
                            temp_int=param['value']
                            if str(temp_int).isdecimal()==True:
                                if temp_int>=18 and temp_int<=30:
                                    bot_c.flag_t=0
                                elif temp_int<18 and bot_c.flag_t==0:
                                    time.sleep(3)
                                    try:
                                        bot_c.bot.sendMessage(bot_c.chat_id, emoji.emojize(f":cold_face: Internal temperature in {room_ID} too low!", use_aliases=True), reply_markup=find_more)
                                        bot_c.flag_t=1
                                    except:
                                        pass
                                elif temp_int>30 and bot_c.flag_t==0:
                                    time.sleep(3)
                                    try:
                                        bot_c.bot.sendMessage(bot_c.chat_id, emoji.emojize(f":hot_face: Internal temperature in {room_ID} too high!", use_aliases=True), reply_markup=find_more)
                                        bot_c.flag_t=1
                                    except:
                                        pass
                        #CHECK ON HUMIDITY VALUE
                        elif parameter=='humidity':
                            hum_int=param['value']
                            if str(hum_int).isdecimal()==True:
                                if hum_int>=30 and hum_int<=55:
                                    bot_c.flag_h=0
                                elif hum_int<18 and bot_c.flag_h==0:
                                    time.sleep(3)
                                    try:
                                        bot_c.bot.sendMessage(bot_c.chat_id, emoji.emojize(f":cactus: Internal humidity in {room_ID} too low!", use_aliases=True), reply_markup=find_more)
                                        bot_c.flag_h=1
                                    except:
                                        pass
                                elif hum_int>55 and bot_c.flag_h==0:
                                    time.sleep(3)
                                    try:
                                        bot_c.bot.sendMessage(bot_c.chat_id, emoji.emojize(f":sweat_drops: Internal humidity in {room_ID} too high!", use_aliases=True), reply_markup=find_more)
                                        bot_c.flag_h=1
                                    except:
                                        pass
                        #CHECK ON AQI VALUE
                        elif parameter=='AQI':
                            aqi_int=param['value']
                            if str(aqi_int).isdecimal()==True:
                                if aqi_int<100:
                                    bot_c.flag_a==0
                                elif aqi_int>=100 and bot_c.flag_a==0:
                                    time.sleep(3)
                                    try:
                                        bot_c.bot.sendMessage(bot_c.chat_id, emoji.emojize(f":red_circle: Internal AQI in {room_ID} too high!", use_aliases=True), reply_markup=find_more)
                                        bot_c.flag_a=1
                                    except:
                                        pass
    
                        try:
                            emo=bot_c.emoji_dic[parameter]
                        except:
                            emo=":small_orange_diamond:"
                        value=str(param['value'])
                        unit=param['unit']
                        bot_c.strin=(bot_c.strin+'\t'+emo+'\t'+parameter+': '+value+' '+unit+'\n')
                        parami=(parami+', '+param['parameter'])
                        bot_c.strin_info=(bot_c.strin_info+'\t\t\t\t'+emo+'\t'+parameter+'\n')
                try:
                    vap_pres=(hum_int/100)*6.105*np.exp(17.27*((temp_int)/(237+temp_int)))
                    app_temp=temp_int+0.33*(vap_pres)-4
                    bot_c.strin=(bot_c.strin+'\t:sunny:\tapparent temperature: '+str("%.2f" %app_temp)+' C\n')
                except:
                    pass
    
                bot_c.strin= (bot_c.strin+'\n')
                bot_c.strin_info= (bot_c.strin_info+'\n')
                #print(bot_c.strin_info)
    
            ##GET ACTUAL CONDITIONS FOR A ROOM
            if bot_c.entered_room_flag==1: #now you are in a room
                bot_c.devices_string=''
                bot_c.room_strin=''
                room_name=bot_c.entered_room
                room=bot_c.name_id_dic[room_name] #ID
    
                room_conditions=requests.get(bot_c.catalogue_url+'/rooms/'+room).json()
                try:
                    room_last_update=room_conditions['last_update']
                except:
                    room_last_update='None'
                devices_list=requests.get(bot_c.catalogue_url+'/rooms/'+room+'/devices').json()
                dev_list_keyboard=[]
                bot_c.dev_name_list=[]
                for i in devices_list:
                    bot_c.dev_name_list.append(i['sensorID'])
                    bot_c.devices_string=(bot_c.devices_string+i['sensorID']+', ')
                bot_c.devices_string=bot_c.devices_string[:-2]
    
                for i in bot_c.dev_name_list:
                    dev_list_keyboard=dev_list_keyboard+[[InlineKeyboardButton(text=emoji.emojize(f':small_blue_diamond:{i}', use_aliases=True), callback_data=i)]]
                dev_list_keyboard=dev_list_keyboard+[[InlineKeyboardButton(text=emoji.emojize(':back:\tBACK', use_aliases=True), callback_data='back')]]
                bot_c.dlk=InlineKeyboardMarkup(inline_keyboard=dev_list_keyboard)
                try:
                    emo_room=bot_c.emoji_dic[room_name]
                except:
                    emo_room=':house:'
                bot_c.room_strin=(bot_c.room_strin+emo_room+'\t'+room_name+':\n')
                bot_c.room_strin=(bot_c.room_strin+'\t:hourglass:\tLast update: '+room_last_update+'\n')
                for devices in room_conditions['devices']:
                    hum_int='NaN'
                    temp_int='NaN'
                    for param in devices['parameters']:
                        parameter=param['parameter']
                        #for app_temp
                        if parameter=='temperature':
                            temp_int=param['value']
                            #for app_temp
                        elif parameter=='humidity':
                            hum_int=param['value']
                        try:
                            emo=bot_c.emoji_dic[parameter]
                        except:
                            emo=":small_orange_diamond:"
                        value=str(param['value'])
                        unit=param['unit']
                        bot_c.room_strin=(bot_c.room_strin+'\t'+emo+'\t'+parameter+': '+value+' '+unit+'\n')
                    try:
                        vap_pres=(hum_int/100)*6.105*np.exp(17.27*((temp_int)/(237+temp_int)))
                        app_temp=temp_int+0.33*(vap_pres)-4
                        bot_c.room_strin=(bot_c.room_strin+'\t:sunny:\tapparent temperature: '+str("%.2f" %app_temp)+' C\n')
    
                    except:
                        pass
                bot_c.room_strin= (bot_c.room_strin+'\n')
                bot_c.entered_room_flag=0
    
            if bot_c.restart==1:
                flag_a=0
                flag_t=0
                flag_h=0
                bot_c.api_create(latitude=41.9109, longitude=12.4818)
                bot_c.restart=0


        #time.sleep(5)