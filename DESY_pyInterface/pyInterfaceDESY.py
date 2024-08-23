#from connectArduino import *
#from DB import *
import sys
import threading
import datetime
import requests
import serial
import time
import random

#Write to database
def send2DB(sensors, values, ts):
        try:
            time.sleep(0.70)
            post_params = ( ('db', 'testInflux'), )
            for i in range(len(sensors)):
                data_sent = sensors[i]+' value='+str(format(values[i], '.2f'))+' '+str(ts)
                #print(data_sent)
                response_db = requests.post('https://influx-prod-24-prod-eu-west-2.grafana.net', params=post_params, data=data_sent)
                #print(response_db)
        except:
            print("Error while connecting to Grafana")

# reading and formatting lists of data
def readData(arduino):
    nsens = arduino.readline().decode().split() #read number of sensors
    nHYT = int(nsens[1])
    nNTC = int(nsens[3])
    valsens = ("").split()
    valsens = ("").split()
    temp = arduino.readline().decode().split()
    hum = arduino.readline().decode().split()
    dew = arduino.readline().decode().split()
    valflow = arduino.readline().decode().split()
    sensname = ("").split()
    for i in range(nHYT):
        valsens.append(temp[i + 1])
        valsens.append(hum[i + 1])
        valsens.append(dew[i + 1])
        sensname.append(f'tempHYT{i}')
        sensname.append(f'humHYT{i}')
        sensname.append(f'dewHYT{i}')
    for i in range(nNTC):
        valsens.append(temp[i + nHYT + 1])
        sensname.append(f'NTC{i}')
    sensname.append("flowmeter")
    valsens.append(valflow[1])
    return sensname, valsens


def mainLoop(comport, baudrate, testmode):
    shutdown = False 
    arduino = serial.Serial(comport, baudrate, timeout=0.1) 
    stringOut = arduino.readline().decode()
    if "Sending data to PC" in stringOut:
        sensOut, valOut = readData(arduino)
        ts = time.time()
        send2DB(sensOut, valOut, ts)
        if testmode:
            print(sensOut,valOut,ts,sep="   ;   ")
            sizesens = len(sensOut)
            sizeval = len(valOut)
            print(f'N of sensors: {sizesens}        N of values: {sizeval}\n')
    if random.randrange(100) > 90 :
        co2state = "CO2_RUN"
    elif random.randrange(100) > 90:
        co2state = "CO2_FAIL"
    else:
        co2state = "CO2_ERROR"
    if testmode:
        print(f"CO2_state: {co2state}\n")
    arduino.write(co2state.encode())
    # may add a condition/signal to stop the script (not sure if needed)
    return shutdown

if __name__ == "__main__":
    shutdown = False
    testmode = True
    while not shutdown:
        shutdown = mainLoop('/dev/cu.usbmodem14201', 115200, testmode)