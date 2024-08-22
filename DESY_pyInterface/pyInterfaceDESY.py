from connectArduino import *
from DB import *
import sys
import threading
import datetime

if __name__ == "__main__":

    arduino = Arduino()
    arduino.connect()

    influx = DB()
    influx.logging()

def mainLoop():
    shutdown = False
    
    if shutdown:
        return True
    else:
        return False

if __name__ == "__main__":
    endloop = False
    while not endloop:
        endloop = mainLoop()