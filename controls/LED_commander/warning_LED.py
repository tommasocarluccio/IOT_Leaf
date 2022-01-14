import time
import sys
from etc.warning_class import *


if __name__ == '__main__':
    conf=sys.argv[1]
    connected_flag=False
    c=warningControl(conf)
    clientID=c.conf_content['clientID']
    while not c.setup(clientID):
        print("Try again..")
        time.sleep(10)
    while True:
        time.sleep(1)