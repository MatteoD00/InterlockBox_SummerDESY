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
            post_params = ( ('db', 'test_PetalColdbox'), )
            for i in range(len(sensors)):
                data_sent = sensors[i]+' value='+str(format(values[i], '.2f'))+' '+str(ts)
                print(data_sent)
                response_db = requests.post('http://atlasmonitoring.desy.de:8086'+'/write', params=post_params, data=data_sent)
                print(response_db)
            return True
        except:
            print("Error while connecting to Grafana")
            return False


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
    hv_intlk = arduino.readline().decode().split()
    hv_on = arduino.readline().decode().split()
    sensname = ("").split()
    for i in range(nHYT):
        valsens.append(float(temp[i + 1]))
        valsens.append(float(hum[i + 1]))
        valsens.append(float(dew[i + 1]))
        sensname.append(f'tempHYT{i}')
        sensname.append(f'humHYT{i}')
        sensname.append(f'dewHYT{i}')
    for i in range(nNTC):
        valsens.append(float(temp[i + nHYT + 1]))
        sensname.append(f'NTC{i}')
    sensname.append("flowmeter")
    valsens.append(float(valflow[1]))
    sensname.append('hv_intlk')
    valsens.append(int(hv_intlk[1]))
    sensname.append('hv_on')
    valsens.append(int(hv_on[1]))
    return sensname, valsens


def mainLoop(arduino, testmode, testCO2):
    shutdown = False 
    stringOut = arduino.readline().decode()
    if "Sending data to PC" in stringOut:
        sensOut, valOut = readData(arduino)
        ts = int(time.time())*1000000000
        successDB = send2DB(sensOut, valOut, ts)
        if testmode:
            print(sensOut,valOut,ts,sep="  ;   ")
            sizesens = len(sensOut)
            sizeval = len(valOut)
            print(f'N of sensors: {sizesens}        N of values: {sizeval}\n')
        """if not successDB:
            try:
                send2DB(["testSignal1"],[0],int(time.time())*1000000000)
                print('2nd atttemp')
            except:
                print('2nd attempt not working')"""
    #Randomize CO2 state simulating an accidental failure for cooling --> Probably still to improve this part
    co2status = "CO2_RUN"
    delay=0.
    if testCO2 :
        if random.randrange(100) < 10 :
            co2status = "CO2_FAIL"
            if random.randrange(100) < 10 :
                co2status = "CO2_ERROR"
            delay=2.
    if testmode:
        print(f"CO2_state: {co2status}\n")
    arduino.write(co2status.encode())
    if delay>0:
        time.sleep(delay)
    # may add a condition/signal to stop the script (not sure if needed)
    return shutdown

if __name__ == "__main__":
    shutdown = False
    testmode = True
    testCO2 = True
    arduino = serial.Serial('/dev/ttyACM0', 115200, timeout=3)
    time.sleep(5)
    while not shutdown:
        shutdown = mainLoop(arduino, testmode, testCO2)
        #time.sleep(1.) #added to match arduino delay