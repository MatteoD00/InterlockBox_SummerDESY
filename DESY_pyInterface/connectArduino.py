# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 16:52:25 2023

@author: oielsu
version: 1.0
"""

import serial
import time
import threading
import numpy as np
import datetime


class Arduino:
  
 array=[]
 running=True
 keyWord1="MQTT:"
 keyWord2="#MQTT:"
 keyWordList=["RH","Temp","DP","HVon","ATemp"]
 locationTemps=["Top,Bot,Below,Frame,EoSp,EoSs"]
 tempTop=0
 tempBot=0
 tempBelow=0
 rhTop=0
 rhBot=0
 rhBelow=0
 dewPointTop=0
 dewPointBot=0
 dewPointBelow=0
 tempFrame=20
 tempEoSF=10
 tempEoSB=10
 stop=False
 HvOn=False
 hvStatus="OFF"
 doorStatus="unlock"
 waitToRead=False
  
 
 def connect(self):
     self.arduino = serial.Serial("/dev/cu.usbmodem14201",115200)
     self.stop=False
     self.running=True
  
 
 def setSerialCom(self):
     self.serial=serial
     
 def close(self):
     self.arduino.close()
     self.running=False
 
 def handle_data(self):
    #print(self.array)
    print("----------------------------")
    print("temp top "+str(self.tempTop))
    print("rh top "+str(self.rhTop))
    print("dp top "+str(self.dewPointTop))
    print("frame "+str(self.tempFrame))
    print("eosf "+str(self.tempEoSF))
    print("eosb "+str(self.tempEoSB))
    print("hv "+str(self.hvStatus))
    print("door "+str(self.doorStatus))
    print("dead "+str(self.stop))
    print("showing data")

 def setVariables(self,location,measureType,value):
     if(location=="PetalBox_Top"):
         if(measureType==self.keyWordList[0]):
            self.rhTop=float(value)
         elif(measureType==self.keyWordList[1]):
            self.tempTop=float(value)
         elif(measureType==self.keyWordList[2]):
            self.dewPointTop=float(value)
     elif(location=="PetalBox_Bot"):
         if(measureType==self.keyWordList[0]):
            self.rhBot=float(value)
         elif(measureType==self.keyWordList[1]):
            self.tempBot=float(value)
         elif(measureType==self.keyWordList[2]):
            self.dewPointBot=float(value)
     elif(location=="PetalBox_Below"):
         if(measureType==self.keyWordList[0]):
            self.rhBelow=float(value)
         elif(measureType==self.keyWordList[1]):
            self.tempBelow=float(value)
         elif(measureType==self.keyWordList[2]):
            self.dewPointBelow=float(value)
     elif(location=="PetalBox_Frame"):
             if(measureType==self.keyWordList[4]):
                self.tempFrame=float(value)
     elif(location=="PetalBox_EoS_F"):
             if(measureType==self.keyWordList[4]):
                self.tempEoSF=float(value)
     elif(location=="PetalBox_EoS_B"):
             if(measureType==self.keyWordList[4]):
                self.tempEoSB=float(value)

     
     self.dewPointTop=self.getDewPoint(self.tempTop,self.rhTop)
     self.dewPointBelow=self.getDewPoint(self.tempBelow,self.rhBelow)
     self.dewPointBot=self.getDewPoint(self.tempBot,self.rhBot)

 
 def setValues(self,dataString):
     location=""
     dataSplit=dataString.split()
     #print(dataSplit)
     if len(dataSplit)>0:

       if(dataSplit[0] == self.keyWord1 or dataSplit[0] == self.keyWord2):
         subData=dataSplit[3].split(",")
         if(subData[0]=="ATemp"):
             if(len(subData)==4):
              location=(subData[1].split("="))[1]
              value=dataSplit[4].split(",")[2].split("=")[1]
         else:
          if(len(subData)==5):
           location=(subData[1].split("="))[1]
           value=(dataSplit[4].split("="))[1]
         if(location!=""):
          self.setVariables(location,subData[0],value)
       elif(dataSplit[0]=="HV_Status:"):
           if(dataSplit[1]=="HV_ON"):
            self.hvStatus="ON"
           if(dataSplit[1]=="HV_OFF"):
            self.hvStatus="OFF"
       elif(dataSplit[0]=="Door_Status:"):
           if(dataSplit[1]=="DOOR_Closed"):
            self.doorStatus="unlock"
           if(dataSplit[1]=="DOOR_LOCKED"):
            self.doorStatus="lock"
       
       
 def getValues(self):
    "returns dictionary with the variables"
    values={
        "rhTop":self.rhTop,
        "rhBot":self.rhBot,
        "rhBelow":self.rhBelow,
        "tempTop":self.tempTop,
        "tempBot":self.tempBot,
        "tempBelow":self.tempBelow,
        "dewPointTop":self.dewPointTop,
        "dewPointBot":self.dewPointBot,
        "dewPointBelow":self.dewPointBelow,
        "tempFrame":self.tempFrame,
        "tempEosF":self.tempEoSF,
        "tempEosB":self.tempEoSB,
        "HvOn":self.hvStatus,
        "door":self.doorStatus,
        "arduinoDead":self.stop}
    return values
          
 def read_from_port(self):
    while self.running==True:
        try:
            byteRead=self.arduino.in_waiting()
            if (byteRead>0):
             self.stop=False
             text=self.arduino.readline().decode('utf-8','ignore')
             self.setValues(text)
        except:
            self.stop=True
            

 def getDewPoint(self,temp,rh):
      A = 6.1121
      B= 17.966
      C = 247.15
      D = 234.5
      np.seterr(divide = 'ignore')
      gamma=np.log((rh/100)*np.exp((B-(temp/D))*(temp/(C+temp))))
      
      if(np.isinf(gamma)):
          dp=-100
      else:
          dp=(C*gamma)/(B-gamma)
      return dp
  
 def writeOrder(self,command):
      self.arduino.write(command.encode())
    
 def writeHv(self,order):
     isOK=False
     self.arduino.flushInput()
     if(order=="ON"):
      self.writeOrder("CMD.HV.ON\n")
      caenStatus="ON"
     elif (order=="OFF"):
         self.writeOrder("CMD.HV.OFF\n")
         caenStatus="OFF"
     else:
         print("invalid order, use on/off")

 
 def writeLock(self,order):
     isOK=False
     self.arduino.flushInput()
     if(order=="ON"):
      self.writeOrder("CMD.DOOR.LOCK\n")
     elif (order=="OFF"):
         self.writeOrder("CMD.DOOR.UNLOCK\n")
     else:
         print("invalid order, use on/off")

 
 def getStatusHv(self):
     self.arduino.reset_input_buffer()
     self.writeOrder("GET.PETALBOX\n")
     
     status=""
     found=False
     actualTime=datetime.datetime.now()
     waitTime=actualTime + datetime.timedelta(seconds=30)
     while (found==False and actualTime<waitTime):
      try:
         status=self.arduino.readline().decode('utf-8','ignore')
      except:
          pass
      actualTime=datetime.datetime.now()
      if("HV_Status") in status:
          found=True
          if("HV_OFF") in status:
              caenStatus="OFF"
          elif ("HV_ON") in status:
              caenStatus="ON"
          elif ("HV_Emer") in status:
              caenStatus="interlock_on"
          elif ("HV_Emergency") in status:
                  caenStatus="interlock_on"
      else:
          caenStatus="Error"
     
     return caenStatus
 
 def getStatusLock(self):
      self.arduino.reset_input_buffer()
      self.writeOrder("GET.PETALBOX\n")
      found=False
      status=""
      actualTime=datetime.datetime.now()
      waitTime=actualTime + datetime.timedelta(seconds=30)
      while (found==False and actualTime<waitTime):
       try:
        status=self.arduino.readline().decode('utf-8','ignore')
        #print(status)
       except:
           pass
       actualTime=datetime.datetime.now()
       if("Door_Status") in status:
           found=True
           if("DOOR_Closed") in status:
               doorStatus="unlock"
           elif ("DOOR_LOCKED") in status:
               doorStatus="lock"
       else:
               doorStatus="error"
               
      return doorStatus
 







