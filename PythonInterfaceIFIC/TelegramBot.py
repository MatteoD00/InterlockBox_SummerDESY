# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 13:10:31 2023

@author: oielsu
"""

import requests

class TelegramBot:
    
    "put the chatID and the token"
    token=""
    chatID=""
    
    def _init_(self):
        pass
    
    
    def sendTest(self,message):
        sendText='https://api.telegram.org/bot' + self.token + '/sendMessage?chat_id=' + self.chatID + '&parse_mode=Markdown&text=' + message
        
        response=requests.post(sendText)
        
        return response.json()["ok"]
    
    def presentacion(self):
        message="Hola\nSoy Schrodi, y me voy a encargar de avisaros de los problemas que puedan surgir en la comunicacion entre el arduino y el programa"
        message+="\nDe momento solo voy a informar de los fallos, pero puedo avisar de cuando empiezan y acaban los test"
        message+="\nLas sugerencias seran atentidas cuando este la beta lista \U0001F600"
        return self.sendTest(message)
        
    def testEnd(self):
        message="TEST FINISHED, YOU CAN OPEN THE DOOR NOW \U0001F44D"
        return self.sendTest(message)
    
    def arduinoConnLost(self):
        message=("\U000026A0 \U0001F631 CONNECTION WITH ARDUINO LOST, PLEASE STOP ARDUINO AND INITIATE MANUAL STOP \U0001F631 \U000026A0")
        return self.sendTest(message)
    
    def temperatureReached(self):
        message=("\U000026A0 TEMPERATURE REACHED INITIATE MANUAL STOP \U000026A0")
        return self.sendTest(message)
    
    def lvConnLost(self,opc):
        if (opc=="normal"):
            message=("LV CONNECTION LOST,PLEASE CHECK USB,STOPPING TEST")
        else:
            message=("\U000026A0 \U0001F631 LV CONNECTION LOST STOPING TEST \U0001F631 \U000026A0")
        return self.sendTest(message)
    
    def pressureFail(self):
        message=("MARTA PUMP VALUES OUT OF RANGE. MARTA HAS BEEN STOPPED FOR SAFETY REASONS")
        message+=("/nINITIATE SHUTDOWN PROCESS")
        return self.sendTest(message)
    
    def eosTempHigh(self):
        message=("\U000026A0 EOS TEMPERATURE TOO HIGH, STOPPING TEST \U000026A0")
        return self.sendTest(message)
    
    def sensorsFail(self):
        message=("\U000026A0 SENSORS FAILURE, STOPPING TEST \U000026A0")
        return self.sendTest(message)   
    
    def caenCheck(self):
        message=("\CAEN HAS NOT STARTED, PLEASE CHECK IT")
        return self.sendTest(message)  

        


