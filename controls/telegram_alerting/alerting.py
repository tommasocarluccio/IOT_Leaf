import json
import requests
import time
import sys
from etc.warning_class import *


if __name__ == '__main__':
    conf=sys.argv[1]
    connected_flag=False
    clientID="warning_control"
    c=warningControl(conf)
    while not c.setup(clientID):
        print("Try again..")
        time.sleep(10)
    while True:
        time.sleep(1)