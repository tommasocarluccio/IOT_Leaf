import json
import random

class TipsHandler():
    def __init__(self,general_tips="data/general_tips.txt",tips="data/tips.json"):
        self.general_tips=self.load_txt(general_tips)
        self.tips=json.load(open(tips,"r"))

    def load_txt(self,filename):
        with open(filename) as f:
            content = f.readlines()
        return content

    def new_tip(self):
        return random.choice(self.general_tips)

    def param_tip(self,param,status):
        parameter=self.tips.get(param)
        tips_list=parameter[status]
        return random.choice(tips_list)
