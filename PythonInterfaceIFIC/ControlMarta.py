# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 09:48:19 2023

@author: oielsu
"""

from modbusMARTA import *
from PyQt6 import QtCore

class ControlMarta:
    
    marta=Marta()
    status=0
    fixFlow=False
    controlTempMax=25.0
    controlMode=False
    start=False
    stop=False
    ciclos=1
    numActualCiclo=1
    minTemp=20
    maxTemp=20
    
    "Min and Max pressure for MARTA co2 pump"
    MINP=1.2
    MAXP=4.5 
    "put marta ip"
    MARTA_IP=""
    
    
    controlTemp=24

    

    def __init__(self):
        pass
    #establece el estado de marta actual
    def martaSetStatus(self):
        self.status = self.marta.get_status()
    
    def martaGetStatus(self):
        return self.status
    
    def setMinTemp(self,temp):
        self.minTemp=temp
        
    def setMaxTemp(self,temp):
            self.maxTemp=temp
        
    #conecta marta
    def connectToMarta(self):
     self.marta.connect(self.MARTA_IP)
     self.martaSetStatus()
     
     #para marta
    def stopMARTA(self):
      self.marta.stop_marta(self.fixFlow)
      self.martaSetStatus()
      print("parando marta")
     
      
     #sets el setpoint
    def setTemperature(self,temp):
     temperature=round(temp,1)
     temperatureSP=round(self.marta.get_temp_setpoint(),1)
     if(temperatureSP!=temperature):
          self.marta.set_temp_setpoint(temperature)
    
    #sets el flow
    def setFlow(self,flow):
     self.fixFlow=True
     self.marta.set_flow_setpoint(flow)
    
    #sets pump speed
    def setSpeed(self,speed):
     self.fixFlow=False
     self.marta.set_speed_setpoint(speed)
     
     #start marta
    def startMARTA(self):
     self.marta.start_chiller(self.fixFlow)
     self.status=self.marta.get_status()
     if(self.status!=2 or self.status!=3):
          QtCore.QTimer.singleShot(240000, self.startCO2)
    
    def startCO2(self):
        self.marta.start_co2(self.fixFlow)


    def setSetPointCooling(self):
         if(self.stop==False):
          temperature=round(self.minTemp,1)
          self.marta.set_temp_setpoint(temperature)
         else:
             self.stopMARTA()
        
    def setSetPointHeating(self):
        if(self.numActualCiclo<=self.ciclos and self.stop==False):
         temperature=round(self.sp_maxTemp,1)
         #self.marta.set_temp_setpoint(temperature)
         print("ciclo:"+str(self.numActualCiclo))
         self.numActualCiclo+=1
        else:
            self.stopMARTA()
        
    def updateControlTemp(self,maxTemp):
        if (self.controlMode == False):
         self.controlTempMax=round(self.controlTempMax,1)
         self.controlMode=True
         self.stop=False
        elif (maxTemp!=round(self.controlTempMax,1)):
         self.controlTempMax=round(self.controlTempMax,1)
         
    def getParameter(self,param):
        return self.marta.getattribute(param)
    
    def getSetPoint(self):
        return self.marta.get_temp_setpoint()
    
    def getFLow(self):
        return self.marta.get_flow_setpoint()
    
    def getSpeed(self):
        return self.marta.get_speed_setpoint()
    
    def controlDewPointRH(self,dp,rh):
        tt06=self.marta.getattribute("TT06_CO2")
        tt05=self.marta.getattribute(("TT05_CO2"))
        minT=min(tt06,tt05)
        if(minT<0):
         if(dp<1.2*minT):
            return True
         else:
            return False
        else:
            if(dp<0.8*minT):
               return True
            else:
               return False  
        
    def controlPumpP(self):
        pt02=self.marta.getattribute("PT02_CO2")
        pt01=self.marta.getattribute("PT01_CO2")
        dp03=pt02-pt01
        if(dp03>self.MINP and dp03<self.MAXP):
            return True
        else:
            return False
         
         
         
    "---------------------------- ver si hacen falta-------------------------------------------------------"

    
    def updateGraphana():
        self.mqtt.setMartaValuesInGraphana(self.marta,"MARTA_APP/Data")
    
    
          

    "-------------------------------------------------------------------------------------"
    "-------------------------------------------------------------------------------------"
    def getStop(self):
        return self.stop
    
    
    def setMqtt(self,mqtt):
        self.mqtt=mqtt
        
    def getStart():
        return self.start
    def setStart(start):
        self.start=start
