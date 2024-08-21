# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 14:06:20 2023

@author: oielsu
version:0.9.2
"""

"""
teoria itsdaq, se escribe el cold_characterisation, y entonces itsdaq escribe starting
cuando termina escribe completed. Hay que ver donde se configura eso
"""


from PyQt6 import uic,QtWidgets,QtCore,QtGui
from connectArduino import *
from ControlMarta import *
from Mtti import *
from SetingWindow import *
#from MartaEnvironment import *
#from MttiEnvironment import *
from DB import *
import sys
import threading
from TelegramBot import*
import bgImage
import datetime
qtCreatorFile = "gui/MainWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
    """falta de marta:

        app: hacer try catch del influx,si no va lanza error y casca el programa"""
    
    marta=ControlMarta() 
    #marta=MartaEnvironment()
    mtti=Mtti()
    #mtti=MttiEnvironment()
    arduino=Arduino()
    
    influx=DB()
    bot=TelegramBot()


    timerUpdateDewPoint = QtCore.QTimer()
    timerUpdateDewMartaParams = QtCore.QTimer()
    timerUpdateDewPointMarta =QtCore.QTimer()
    timerCheckMartaStatus = QtCore.QTimer()
    timerGetDataArduino= QtCore.QTimer()
    timerCheckArduino= QtCore.QTimer()
    timerCheckLV = QtCore.QTimer()
    timerCheckEndTest = QtCore.QTimer() 
    timercheckDp_martaOff = QtCore.QTimer() 
    timerCheckParam = QtCore.QTimer()
    timercheckEmergency = QtCore.QTimer()
    timercheckDpOff = QtCore.QTimer()
    timerCheckHV = QtCore.QTimer()
    

    T_SHUTDOWN=16
    T_EMERGENCY_SHUTDOWN=15
    T_SHUTDOWN_DP_OFF=15
    T_LV_SHUTDOWN=10
    
    arduinoDead=False
    shutdown_ok=False
    startMarta=False
    status=5
    stopMarta=False
    """"varible to determine which stop process should apply
           0-----> dp failure
           1-----> another type of failure
           2-----> normal process"""
    emergency=2
    startTest=False
    
    "tiempos de checkeo de parametros"
    "en ms----------------------------------"
    TIME_ARDUINO=10*1000
    TIME_MARTA=5*60*1000
    TIME_DEWPOINT=10*1000
    TIME_MARTA_PARAMS=30*1000
    TIME_CHECK_LV=30*1000
    TIME_TO_HV=30*1000
    
    TIME_EMERGENCY_SHUTDOWN=30*1000
    TIME_FULLHEAT=30*1000
    TIME_DP_SHUTDOWN=30*1000
    "en min,multiplos de 5min"
    TIMEOUT=60
    TIME_CHECK_END_TEST=3*60*1000
    TIME_PARAMS=10*1000
    
    "en seg----------------------------------"
    TIME_TO_STABLISH_MARTA_COND=6*60
    timeToStablish=0
    "-----------------------------------------"
    "inicializar dp y hr a valores altos para version final"
    dp=100
    hr=100
    rhTop=100
    rhBot=100
    rhBelow=100
    dewPointBelow=20
    dewPointTop=20
    dewPointBot=20
    conectionsCounter=0
    isDP=False
    tempEosF=10
    tempEosB=10
    T_EOS_MAX=28
    SENSOR_LIMIT=-45
    SENSOR_LIMIT_SUP=26
    T_EOS_LIMIT=-45
    martaFail=False
    dpFail=False
    temp=25
    "-------------Temp que queremos llegar en el test, (-34 o -33)----------------"
    TEST_TEMPERATURE_COLD=10
    TEST_TEMPERATURE_HOT=15
    "------------------------------"
    setHV=False
    setLV=False
    HV=False
    LV_on=False
    DAQ_on=False
    LV_ok=False
    v1=11
    v2=11
    v3=12
    lvConLost=False
    "intentos de hablar con hv antes del fallo y aviso por bot"
    MAXCONNECTIONSHV=4
    MAXCONNHV_BOT= MAXCONNECTIONSHV-1
    "-----------------------------------------------"
    hvConTry=0
    isHvTimerStop=False
    doorStatus="unlock"
    isDoorLock=False
    hvStatus="OFF"
    caenInterlock=False
    
    DP_SB=10
    waitingToFinish=False
    startEndTest=False
    started=False
    startHeatTest=False
    startColdTest=False
    isManualTest=False
    isColdDone=False
    isTestFinished=False
    isShutdown=False
    isTimerEndTest=False
    
    itsdaqCounter=0
    isOptionsOpen=False
    
    "debug"
    debugCounter=0
    statusDebug=1
    debugTemp=-35
    i=0
    debufTestCompleted=False
    
    "----------------------------------------"
    DPGREEN=-35
    DPBLUE=6
    
    def __init__(self): 
        QtWidgets.QMainWindow.__init__(self) 
        Ui_MainWindow.__init__(self)
        self.setupUi(self) 
        
        
        
        "------------arduino-------------------"
        self.arduino.connect()
        self.thread = threading.Thread(target=self.arduino.read_from_port,args=(), daemon=True)
        self.thread.start() 
        self.timerGetDataArduino.timeout.connect(lambda:getArduinoData())
        self.timerGetDataArduino.start(self.TIME_ARDUINO)
        self.timerCheckArduino.timeout.connect(lambda:checkArduino())
        self.timerCheckArduino.start(self.TIME_ARDUINO+1000)
        "---------------------------------------"
        
        
        "-----------------marta--------------------"
        self.timerCheckMartaStatus.timeout.connect(lambda:showStatus())
        self.timerCheckMartaStatus.start(self.TIME_MARTA)
 
        
        "-----------------fuente--------------------"
        self.mtti.connect()
        self. mtti.write_termination("\n")
        self.mtti.turn_off(1)
        self.mtti.turn_off(2)
        self.mtti.turn_on(3)
        self.mtti.set_voltage(1, 11)
        self.mtti.set_voltage(2, 11)
        #self.mtti.set_voltage(3, 12)
        self.lcd_v1.display('{:.02f}'.format(self.v1))
        self.lcd_v2.display('{:.02f}'.format(self.v2))
        self.lcd_v3.display('{:.02f}'.format(self.v3))
        
        self.timerCheckLV.timeout.connect(lambda:checkLV())
        self.timerCheckLV.start(self.TIME_CHECK_LV)
        
        "-----------------DB------------------------"
        self.influx.logging()



        def closeEvent(self, event):
            super(MainWindow, self).closeEvent(event)
            self.arduino.close()
            self.influx.logout()
            print("cerrando ventana")
            
        def openSettings():
            testParams={
                "T_SHUTDOWN":self.T_SHUTDOWN,
                "TEST_TEMPERATURE_HOT":self.TEST_TEMPERATURE_HOT,
                "TEST_TEMPERATURE_COLD":self.TEST_TEMPERATURE_COLD,
                "TIME_ARDUINO":self.TIME_ARDUINO,
                "TIME_MARTA":self.TIME_MARTA,
                "TIME_DEWPOINT":self.TIME_DEWPOINT,
                "TIME_CHECK_LV":self.TIME_CHECK_LV,
                "TIME_MARTA_PARAMS":self.TIME_MARTA_PARAMS,
                "TIME_CHECK_END_TEST":self.TIME_CHECK_END_TEST,
                "TIME_PARAMS":self.TIME_PARAMS,
                "T_EOS_MAX":self.T_EOS_MAX,
                "T_EOS_LIMIT":self.T_EOS_LIMIT,
                "SENSOR_LIMIT":self.SENSOR_LIMIT,
                "SENSOR_LIMIT_SUP":self.SENSOR_LIMIT_SUP,
                "TIMEOUT":self.TIMEOUT
                }
            self.settingsWindow = SettingsWindow(testParams)
            self.settingsWindow.saveClicked.connect(updateTestSettings)
            self.settingsWindow.show()
            self.isOptionsOpen=True
            
        def updateTestSettings(settings):
            print(settings)
            self.T_SHUTDOWN=settings["T_SHUTDOWN"]
            self.TEST_TEMPERATURE_HOT=settings["TEST_TEMPERATURE_HOT"]
            self.TEST_TEMPERATURE_COLD=settings["TEST_TEMPERATURE_COLD"]
            self.TIME_ARDUINO=settings["TIME_ARDUINO"]
            self.TIME_MARTA=settings["TIME_MARTA"]
            self.TIME_DEWPOINT=settings["TIME_DEWPOINT"]
            self.TIME_CHECK_LV=settings["TIME_CHECK_LV"]
            self.TIME_MARTA_PARAMS=settings["TIME_MARTA_PARAMS"]
            self.TIME_CHECK_END_TEST=settings["TIME_CHECK_END_TEST"]
            self.TIME_PARAMS=settings["TIME_PARAMS"]
            self.T_EOS_MAX=settings["T_EOS_MAX"]
            self.T_EOS_LIMIT=settings["T_EOS_LIMIT"]
            self.SENSOR_LIMIT=settings["SENSOR_LIMIT"]
            self.SENSOR_LIMIT_SUP=settings["SENSOR_LIMIT_SUP"]
            self.TIMEOUT=settings["TIMEOUT"]
            self.isOptionsOpen=False
            
            "prueba-------------------"
            self.settingsWindow.close()
            "-----------------------"
        
        def showStatus():
            try:
             self.status=self.marta.martaGetStatus()
             if(self.status==1):
                self.l_info.setText("Conectada")
                self.but_connectMarta.setIcon(QtGui.QIcon('icons/power_on.svg'))
                self.influx.setMARTAstatus("CONECTADA")
             elif(self.status==2):
                self.l_info.setText("CO2 working")
                self.influx.setMARTAstatus("CO2 WORKING")
             elif(self.status==3 and startTest==True):
                self.l_info.setText("Alarmas activadas")
                self.influx.setMARTAstatus("ALARM")
                self.but_connectMarta.setIcon(QtGui.QIcon('icons/power_error.svg'))
                print("----FALLO EN MARTA APAGANDO TEST---")
                self.martaFail=True
                endTest()
             else:
                self.l_info.setText("Error al comunicarse con MARTA") 
                self.martaFail==True
             
            except:   
                self.l_info.setText("Error al comunicarse con MARTA") 
                endtest()
                self.influx.writeError("MARTA COM ERROR")
                self.martaFail==True
                
        def updateParam():
           
           try:
            pt02=self.marta.getParameter("PT02_CO2")
            pt01=self.marta.getParameter("PT01_CO2")
            self.press=pt02-pt01
            self.tSetPoint=self.marta.getSetPoint()
            self.tt06=self.marta.getParameter("TT06_CO2")
            self.tt05=self.marta.getParameter("TT05_CO2")
            self.flow=self.marta.getParameter("FT01_CO2")
            self.temp=self.marta.getParameter("ST04_CO2")
            self.lcd_pump.display('{:.02f}'.format(float(self.press)))
            self.lcd_flow.display('{:.02f}'.format(float(self.flow)))
            self.lcd_tsp.display('{:.02f}'.format(self.tSetPoint))
            self.lcd_t.display('{:.02f}'.format(self.temp))
           except:
              print("error en la comunicación con marta")
              self.influx.writeError("MARTA COM ERROR")
            
           try:
            values={
               "T_SP":float(self.tSetPoint),
               "TT05_CO2":float(self.tt05),
               "TT06_CO2":float(self.tt06),
               "DP03_CO2":float(self.press),
               "FT01_CO2":float(self.flow),
               "ST04_CO2":float(self.temp)}       
            self.influx.updateMartaValues(values)
           except:
             print("error en la comunicación con marta")
             self.influx.writeError("INFLUX COM ERROR")
           
                
        def getArduinoData():
            values=self.arduino.getValues()
            self.rhTop=values["rhTop"]
            self.rhBot=values["rhBot"]
            self.rhBelow=values["rhBelow"]
            self.tempTop=values["tempTop"]
            self.tempBot=values["tempBot"]
            self.tempBelow=values["tempBelow"]
            self.dewPointTop=values["dewPointTop"]
            self.dewPoinBot=values["dewPointBot"]
            self.dewPointBelow=values["dewPointBelow"]
            self.tempFrame=values["tempFrame"]
            self.arduinoDead=values["arduinoDead"]
            self.doorStatus=values["door"]
            self.hvStatus=values["HvOn"]
            self.tempEosF=values["tempEosF"]
            self.tempEosB=values["tempEosB"]

            setMinControlValues()
            setPetalValues()
            self.influx.updateArduinoValues(values)
            

        
        def setPetalValues():
            
            self.lcd_hr_top.display('{:.02f}'.format(self.rhTop))
            self.lcd_hr_bot.display('{:.02f}'.format(self.rhBot))
            self.lcd_hr_below.display('{:.02f}'.format(self.rhBelow))
            self.lcd_t_top.display('{:.02f}'.format(self.tempTop))
            self.lcd_t_bot.display('{:.02f}'.format(self.tempBot))
            self.lcd_t_below.display('{:.02f}'.format(self.tempBelow))
            self.lcd_t_frame.display('{:.02f}'.format(self.tempFrame))
            self.lcd_t_eosp.display('{:.02f}'.format(float(self.tempEosF)))
            self.lcd_t_eoss.display('{:.02f}'.format(float(self.tempEosB)))
            
            
            checkSensorValues()
            
            if(max(self.tempEosF,self.tempEosB)>self.T_EOS_MAX and self.startEndTest==False):
                self.bot.eosTempHigh()
                print("-----------EOS TEMP ELEVADA-----------")
                self.influx.writeError("HIGH EOS T")
                endTest()
                self.startEndTest=True
            
            if(self.doorStatus=="lock"):
                self.lock_icon.setIcon(QtGui.QIcon('icons/lock.svg'))
            elif(self.doorStatus=="unlock"):
                self.lock_icon.setIcon(QtGui.QIcon('icons/lock_open.svg'))
                
            if(self.dp<self.DPGREEN):
                self.hr_icon.setIcon(QtGui.QIcon('icons/humidity_low.svg'))
            elif(self.dp>self.DPGREEN and self.dp<self.DPBLUE):
                self.hr_icon.setIcon(QtGui.QIcon('icons/humidity_mid.svg'))
            else:
                self.hr_icon.setIcon(QtGui.QIcon('icons/humidity_high.svg'))
    
            if(self.hvStatus=="ON"):
                self.hv_icon.setEnabled(True)
                "----añadido,ver si funciona----"
                self.HV=True
            elif(self.hvStatus=="OFF"):
                self.hv_icon.setEnabled(False)
                "----añadido,ver si funciona----"
                self.HV=False
                
        def checkSensorValues():
            
            sensorFail=0

            if(self.tempEosB<self.T_EOS_LIMIT and self. tempEosF<self.T_EOS_LIMIT):
                print("eos sensor malfuction")
                self.bot.sensorsFail()
                self.influx.writeError("EOS SENSOR FAIL")
                endTest()
            if(self.tempBelow<self.SENSOR_LIMIT or self.tempBelow>self.SENSOR_LIMIT_SUP):
                sensorFail+=1
            if(self.tempTop<self.SENSOR_LIMIT or self.tempTop>self.SENSOR_LIMIT_SUP):
                sensorFail+=1
            if(self.tempBot<self.SENSOR_LIMIT or self.tempBot>self.SENSOR_LIMIT_SUP):
                sensorFail+=1
            
            if(sensorFail>=3 and self.startEndTest==False):
                self.bot.sensorsFail()
                print("------FULL SENSOR FAILURE------")
                self.influx.writeError("SENSOR FAILURE")
                endTest()
                self.startEndTest=True
            
        def checkArduino():
            if(self.arduinoDead==True):
                print("perdida de conexion con el arduino")
                self.arduino.close()
                print("-----------------")
                try:
                    if(self.conectionsCounter<2):
                       self.arduino.connect()
                       self.conectionsCounter=0
                       self.arduinoDead=False
                       print("conectando..............")
                    else:
                        if(self.startEndTest==False):
                         print("apagando test")                        
                         self.bot.arduinoConnLost()
                         print("-----conexion con arduino perdida----")
                         emergencyStopProcess()
                         self.startEndTest=True
                        
                except:
                 print("fallo conexion, intentando conectar de nuevo......")
                 self.conectionsCounter+=1
                
           
        def connectMarta():
         self.marta.connectToMarta()
         showStatus()
     
        def setSetpoint():
         self.status=self.marta.martaGetStatus()
         if(self.status==1 or self.status==2):
          tempSP=float(self.spin_tempSetPoint.value())
          self.marta.setTemperature(tempSP)
          self.lcd_tsp.display('{:.02f}'.format(tempSP))
          self.influx.updateMARTAsp(tempSP)
         else:
             self.l_test_info.setText("conectate antes a MARTA")
    
        def abort():
         print("----------APAGANDO MARTA--------------")
         self.marta.stopMARTA()
         self.startTest==False
         self.timerUpdateDewPoint.stop()
         self.timerUpdateDewMartaParams.stop()
         self.timerUpdateDewPointMarta.stop()
         self.timerCheckMartaStatus.stop()
         self.timerGetDataArduino.stop()
         self.timerCheckArduino.stop()
         self.timerCheckLV.stop()
         self.timerCheckEndTest.stop()
         self.timerCheckParam.stop()
         self.timercheckEmergency.stop()
         self.timercheckDpOff.stop()
         self.timerCheckEndTest.stop()
         self.timerCheckHV.stop()
         
         if(self.LV_on==True):
          closeLVChannels()
         self.timercheckDp_martaOff.stop()
         self.mtti.close()
         self.but_startTest.setEnabled(True)
         self.influx.logout()
         self.but_abort_marta.setEnabled(False)
         
         "apertura de lock"
         self.arduino.writeLock("OFF")
         self.lock_icon.setIcon(QtGui.QIcon('icons/lock_open.svg'))
         self.bot.testEnd()
         self.arduino.close()
         
        def stop():
         self.marta.setTemperature(self.T_SHUTDOWN)
         self.timerCheckParam.timeout.connect(lambda:checkParam_shutdown())
         self.timerCheckParam.start(10000)
         print("----------CHECKING SHUTDONW PARAMS-----------")
         
        def checkParam_shutdown():
            maxT=max(self.tt05,self.tt06)
            if(maxT>=self.T_LV_SHUTDOWN and self.LV_on==True):
                if(self.lvConLost==False):
                 closeLVChannels()
                else:
                    abort()
            if(maxT>=(self.T_SHUTDOWN-0.3) and self.lvConLost==False and self.LV_on==False):
                abort()
                
        
        def setMinControlValues():
            self.dp=max([self.dewPoinBot,self.dewPointBelow,self.dewPointTop])
            self.hr=max([self.rhBot,self.rhBelow,self.rhTop])


        
        def checkDewPoint():
           "se checkea el dp para iniciar el chiller,solo util hasta que se inicia"
           
           if(self.dp<1.2*self.marta.getSetPoint()):
              startCooling()
           else:
              print("condiciones para arrancar marta no alcanzadas dp alto")
              self.l_test_info.setText("WAITING FOR LOWER DP......")

          
        def checkMartaConditions():
            "se checkean condiciones de p y dp de marta, se puede ampliar a mas parametros"
                      
            if(self.timeToStablish>=self.TIME_TO_STABLISH_MARTA_COND):
             isDPOk=self.marta.controlDewPointRH(self.dp,self.hr)
             isPressureOk=self.marta.controlPumpP()
             if(isDPOk ==True and isPressureOk==True):
                 self.stopMarta=False
                 self.pump_icon.setIcon(QtGui.QIcon('icons/pump_ok.svg'))
             else:
                 if(isDPOk==True and self.martaFail==False):
                     "fallo de presion,se apaga marta por seguridad"
                     self.stopMarta=True
                     self.marta.stopMARTA()
                     self.martaFail=True
                     self.pump_icon.setIcon(QtGui.QIcon('icons/pump_fail.svg'))
                     endTest()
                     self.martaFail==True
                     self.bot.pressureFail()
                     self.influx.writeError("MARTA PUMP ERROR")
                 else:
                     if(self.martaFail==False and self.dpFail==False):
                      endTest_fullHeat()
                      self.dpFail=True
                      self.influx.writeError("DP FAILURE")
                      

                     
                  
            else:
                self.timeToStablish+=30
            
            print("checkeando condiciones de marta")
            
            
            if(self.startEndTest==False):
             getTemperature()
                
        def getTemperature():
         if(self.startEndTest==False):
            if(self.temp<=self.TEST_TEMPERATURE_HOT and self.setLV!=True and self.HV==False and self.lvConLost==False and self.started==False):
               if(self.startEndTest==False):
                print("----------iniciando LV-----------")
                self.setLV=True
                self.started=True
                startLV()
            elif(self.temp<=self.TEST_TEMPERATURE_COLD and self.startColdTest==True and self.isTestFinished==True and self.lvConLost==False and self.setLV==True and self.started==True):
                QtCore.QTimer.singleShot(self.TIME_TO_HV, checkHVStatus)
                self.isTestFinished=False
                self.waitingToFinish=True
                self.isHvTimerStop=False
                self.influx.setColdCharacterization()
                print("lanzando oneshot para cold")
                
            elif(self.temp>=self.TEST_TEMPERATURE_HOT and self.startHeatTest==True and self.isTestFinished==True and self.lvConLost==False and self.setLV==True and self.started==True and self.isColdDone==True):
                QtCore.QTimer.singleShot(self.TIME_TO_HV, checkHVStatus)
                self.isTestFinished=False
                self.waitingToFinish=True
                self.isHvTimerStop=False
                self.influx.setWarmCharacterization() 
                print("lanzando oneshot para calor")
               
        """-------------------------------------------------------------
           --------------------FUENTES----------------------------------
           -------------------------------------------------------------"""
               
        def startLV():
            if(self.setLV==True):
                print("--------encendiendo LV---------")
                if(self.LV_ok==True and self.LV_on==False and self.lvConLost==False):
                    try:
                     self.mtti.turn_on(1)
                     self.mtti.turn_on(2)
                     #self.mtti.turn_on(3)
                     print("abriendo canales")
                     self.LV_on=True
                     self.lv_icon.setEnabled(True)
                     self.but_manualTest.setEnabled(True)
                    except:
                        connectionLV_lost()

                    
        
        def checkLV():
            print("-------------checkeando LV------------")
            
            getSupplyParams()
            
            self.lcd_v1.display('{:.02f}'.format(self.v1))
            self.lcd_v2.display('{:.02f}'.format(self.v2))
            self.lcd_v3.display('{:.02f}'.format(self.v3))
            
            if(self.v1==self.v2==11 and self.v3==12):
                self.LV_ok=True
            else:
                print("voltajes distinto a normales,cuidado")
            
            if(self.lvConLost==False):
             isLV1_on=self.mtti.is_output_on(1)
             isLV2_on=self.mtti.is_output_on(2)
             isLV3_on=self.mtti.is_output_on(3)
             #isLV3_on=1

             if(isLV1_on==1 or isLV2_on==1):
                self.LV_on=True
                self.lvConLost=False
             else:
                self.LV_on=False
             if(isLV3_on==1):
                self.DAQ_on=True
             else:
                self.DAQ_on=False
                
            values={
                    "LV_CH1":float(self.v1),
                    "LV_CH2":float(self.v2),
                    "LV_CH3":float(self.v3),
                    "LV_ON":self.LV_on,
                    "HV_ON":self.HV} 
            
            if(self.HV==True):
             self.hv_icon.setEnabled(True)
            else:
                self.hv_icon.setEnabled(False)
            
            if(self.LV_on==True):
                self.lv_icon.setEnabled(True)
            else:
                self.lv_icon.setEnabled(False)
                
            self.influx.updateVoltages(values)
            
                
        def getSupplyParams():
            try:
             self.v1=self.mtti.get_voltage_setpoint(1)
             self.v2=self.mtti.get_voltage_setpoint(2)
             #self.v3=self.mtti.get_voltage_setPoint(3)
            except:
                connectionLV_lost()
                
        def connectionLV_lost():
            
            if(self.startTest==True and self.lvConLost==False):
             print("conexion a LV perdida")
             self.influx.writeError("LV CONN LOST")
             if(self.HV==True):
                 self.bot.lvConnLost("danger")
                 emergencyStopProcess()
                 self.lvConLost=True
                 print("aviso por telegram")
                 self.bot.lvConnLost("normal")
             else:
                 if(self.emergency!=2):
                  emergencyStopProcess()
                  self.lvConLost=True
                  print("aviso por telegram")
                  self.bot.lvConnLost("normal")
            
             
        def checkHVStatus():
           print("-------checkeando HV-------------------------")
           if(self.hvConTry<=self.MAXCONNECTIONSHV and self.isHvTimerStop==False):
            status=self.arduino.getStatusHv()
            
            if(self.hvConTry>=self.MAXCONNHV_BOT and self.isHvTimerStop==False):
                self.bot.caenCheck()
                self.but_hvReady.setEnabled(True)
                
            print("hv status: "+str(status))
            if(status=="ON" and self.caenInterlock==False):
                self.hvConTry=0 
                self.l_test_info2.setText("HV CONNECTED......")
                self.HV=True
                self.hv_icon.setEnabled(True)
                self.waitingToFinish=True
                if(self.isTimerEndTest==False):
                 self.timerCheckEndTest.timeout.connect(lambda:checkEndTest())
                 self.timerCheckEndTest.start(self.TIME_CHECK_END_TEST)
                 self.isTimerEndTest=True
                 print("iniciando timer end test")
                if(self.startColdTest==True):
                 "iniciamos el cold characterization"
                 print("----------starting ITSDAQ cold---------")
                 self.l_test_info2.setText("ITSDAQ COLD TEST ONGOING......")
                elif(self.startHeatTest==True):
                  print("--------starting itsdaq hot----------")
                  self.l_test_info2.setText("ITSDAQ HOT TEST ONGOING......") 
                stopHVtimer()
            elif(status=="interlock_on"):
               self.l_test_info2.setText("INTERLOCK ON......")
               print("Interlock On....")
               if(self.hvConTry>=round(self.MAXCONNECTIONSHV/2)):
                   "se manda on al arduino para que podamos leer el estado de la caen"
                   "mientras se apaga dara hv_on, cuando termine de apagarse dará hv_off"
                   self.arduino.writeHv("ON")
                   self.caenInterlock=True
               self.hvConTry+=1
            elif(status=="OFF" and self.caenInterlock==True):
                 self.caenInterlock=False
                 self.HV=False
                 self.hv_icon.setEnabled(False)
                 self.waitingToFinish=False
                 self.hvConTry=0
                 if(self.emergency==0):
                  endTestEmergency()
                 elif(self.emergency==1):
                  emergencyShutDown()
                 else:
                     if(self.startEndTest==True and self.isShutdown==False):
                        "solo se para cuando se acaban los test"
                        endTestHVOff()
                 stopHVtimer()
            else:
                emergencyShutDown()
           else:
                endTest()
                
        def stopHVtimer():
            self.timerCheckHV.stop()
            self.isHvTimerStop=True
            print("timer hv stop")
            
        def stopEndTestTimer():
            self.timerCheckEndTest.stop()
            self.isTimerEndTest=False
            print("timer endtest stop")
            
        def checkEndTest():
            if(self.HV==True and self.isHvTimerStop==False and self.startEndTest==True):
                stopHVtimer()
            if(self.startEndTest==False and self.waitingToFinish==True):
             print("checkeando end test........")
             isCompleted=self.influx.getCompleted()
            
             
             if(isCompleted==True and self.startEndTest==False):
                 print("ITSDAQ FINISHED")
                 self.l_test_info2.setText("ITSDAQ FINISHED......")
                 print("------Start next process----")
                 self.itsdaqCounter=0;
                 self.isTestFinished=True

                 if(self.startHeatTest==True and self.isColdDone==False):
                     self.l_test_info.setText("COOLING......")
                     self.marta.setTemperature(self.TEST_TEMPERATURE_COLD)
                     self.waitingToFinish=False
                     self.startHeatTest=False
                     self.startColdTest=True
                     self.isColdDone=True
                     self.test_icon1.setEnabled(True)
                 elif(self.startColdTest==True and self.isColdDone==True):
                     self.l_test_info.setText("HEATING......")
                     self.marta.setTemperature(self.TEST_TEMPERATURE_HOT)
                     self.startColdTest=False
                     self.startHeatTest=True
                     self.startColdTest=False
                     self.waitingToFinish=False
                     self.test_icon2.setEnabled(True)
                 elif(self.startEndTest==False):
                     self.test_icon3.setEnabled(True)
                     endTest()
                 
             elif(isCompleted==False):
                 print("no ha terminado itsdaq")    
             elif(isCompleted==None):
                 print("ITSDAQ HASN'T FINISHED YET, waiting 5min to check it again")
                 self.l_test_info2.setText("ITSDAQ WORKING......")
                 self.itsdaqCounter+=5;
            
            if(self.itsdaqCounter>60):
                print("SOMETHING IS HAPPINING TO ITSDAQ, PLEASE CHECK IT, END TEST MANUALLY")
                self.l_test_info2.setText("SOMETHING IS HAPPINING TO ITSDAQ, PLEASE CHECK IT, END TEST MANUALLY")
                self.startEndTest=True
                endTest()
            
        def checkDP_shutdown():
            
            if(self.LV_on==True):
                self.setLV=False
                closeLVChannels()
            
            if(self.dp>=(1.2*self.DP_SB)):
                print("----ABORTANDO------")
                abort()

        def fullHeat_shutdown():
            maxT=max(self.tt05,self.tt06)
            
            if(maxT>=self.T_SHUTDOWN_DP_OFF):
                print("----ABORTANDO------")
                abort()
        
        def checkEmergency_shutdown():
            minT=min(self.tt05,self.tt06)
            
            if(self.martaFail==True):
                if(self.HV==True):
                    self.but_abort_marta.setEnabled(True)
                    self.l_test_info2.setText("WAITING TO MANUAL EMERGENCY STOP......")
                else:
                    checkDP_shutdown()
            
            if(minT>=self.T_EMERGENCY_SHUTDOWN and self.HV==True):
                self.bot.temperatureReached()
                self.but_abort_marta.setEnabled(True)
                print("aviso, pulsa emergency stop")
                self.l_test_info2.setText("WAITING TO MANUAL EMERGENCY STOP, PLEASE CHECK HV......")
            elif(minT>=self.T_EMERGENCY_SHUTDOWN and self.HV==False):
                self.but_abort_marta.setEnabled(True)
                print("aviso, pulsa emergency stop")
                self.l_test_info2.setText("WAITING TO MANUAL EMERGENCY STOP......")
             
        def butUser_HVOff():
            self.HV=False
            self.but_abort_marta.setEnabled(False)
            self.but_stopTest.setEnabled(False)
            self.timercheckEmergency.stop()
            stop()
        
        def closeLVChannels():
            if(self.lvConLost==False):
             try:
               print("-------APAGANDO LV-------")
               print("----apagando canales-----")
               self.mtti.turn_off(1)
               self.mtti.turn_off(2)
               self.setLV=False
               self.LV_on=False
               self.lv_icon.setEnabled(False)
             except:
                connectionLV_lost()
            else:
                print("conexion a lv perdida")
        
        def sendITSDAQorder():
            self.but_hvReady.setEnabled(False)
            self.hvConTry=0
            if(self.temp<=self.TEST_TEMPERATURE_COLD):
                self.influx.setColdCharacterization()
            elif(self.temp<=self.TEST_TEMPERATURE_HOT):
                self.influx.setColdCharacterization()
            else:
                print("wait till temp reached")
                
        """------------------------------------------------------------------
               START TEST
        ---------------------------------------------------------------------"""
        
        def startTest():
            
            """
            Conditions to start:
                lock close
                marta on    
            """  
            self.started=False
            self.isColdDone=False
            self.isShutdown=False
            self.isTimerEndTest=False
            self.martaFail=False
            self.dpFail=False
            self.doorStatus="unlock"
            self.caenInterlock=False
            
            "mirar si ventana open"
            if(self.isOptionsOpen==False):
             self.but_options.setEnabled(False)
             self.arduino.writeHv("ON")    
             
            "send command to lock"
            self.arduino.writeLock("ON")
            
            "recheck of the door status"
            self.doorStatus=self.arduino.getStatusLock()
            

            
            if(self.doorStatus=="lock"):
             self.lock_icon.setIcon(QtGui.QIcon('icons/lock.svg'))
             
             self.but_stopTest.setEnabled(True)
             self.but_startTest.setEnabled(False)
            

             self.l_test_info.setText("STARTING......")
             self.l_test_info2.setText("")
             self.timerUpdateDewPoint.timeout.connect(lambda:checkDewPoint())
             self.timerUpdateDewPoint.start(self.TIME_DEWPOINT) 
            
             "iniciar counters y variables"
             self.itsdaqCounter=0
            else:
                self.l_test_info.setText("ACTIVATE LOCK BEFORE START")
                self.l_test_info2.setText("")
            
        def startCooling():
            if(self.status==1 or self.status==2):
                  self.startTest=True
                  self.l_test_info.setText("INITIATE COOLING......")
                  self.l_test_info2.setText("")
                  self.marta.setTemperature(self.TEST_TEMPERATURE_HOT)
            else:
                self.l_test_info.setText("CHECK MARTA STATUS")
                  
                  
            if(self.startTest==True and (self.status==1 or self.status==2)):
                self.but_startTest.setEnabled(False)
                
                print(".........encendiendo marta...........")
                if(self.status==1):
                 self.marta.startMARTA()
                 
                self.pump_icon.setEnabled(True)
                self.pump_icon.setIcon(QtGui.QIcon('icons/pump_ok.svg'))
                updateParam()
                print(".........esperando...................")
                "paramos el control de dp inicial"
                self.timerUpdateDewPoint.stop()

                
                "----------------------------------------------------------------------"
                self.timerUpdateDewMartaParams.timeout.connect(lambda:updateParam())
                self.timerUpdateDewMartaParams.start(self.TIME_PARAMS)
                "-----------------------------------------------------------------------"
                self.timerUpdateDewPointMarta.timeout.connect(lambda:checkMartaConditions())
                self.timerUpdateDewPointMarta.start(self.TIME_MARTA_PARAMS)
                

        """
        --------------------------------------------------------------
                                 END TEST
        --------------------------------------------------------------
        """        
         
            
        def endTest():
             """"
             funcion para iniciar proceso de parada del test
             """
             self.influx.testOff()
             
             
             
             if(self.martaFail==True):
                 self.timerUpdateDewPointMarta.stop()
                 
             
             if(self.startEndTest==False):
              stopHVtimer()
              stopEndTestTimer()
              self.startEndTest=True
              print("--------PARANDO TEST---------")
              self.l_test_info.setText("STOPPING TEST......")
              self.l_test_info2.setText("")
              if (self.HV==True):
                 orderArduino("OFF")
              else:
                 endTestHVOff()
                     

        def startITSDAQTest():
             isReady=self.influx.getReady()
             "isReady=True"
             
             if(isReady!=True):
                 print("-----itsdaq is not ready-------")
                 self.l_test_info.setText("INFLUX_DAQ IS NOT READY......")
                 self.l_test_info.setText("WAIT AND TRY AGAIN......")
             else:
              if(self.LV_on==True):
               self.isManualTest==False 
               self.l_test_info.setText("AUTOMATIC TEST MODE......")
               "si el boton se pulsa el petalo esta listo para el testeo automatico"
               self.influx.setWarmCharacterization() 
               orderArduino("ON")            
               self.but_manualTest.setEnabled(False)
               self.startHeatTest=True
               self.startColdTest=False
        
        def orderArduino(order):
                 self.arduino.writeHv(order)    
                        
                 self.timerCheckHV.timeout.connect(lambda:checkHVStatus())
                 self.timerCheckHV.start(self.TIME_TO_HV)
                 self.isHvTimerStop=False
                 if(order=="OFF"):
                     print("-----apagando HV-------")
                 elif(order=="ON"):
                     print("-----encendiendo HV-------")
             
        def endTestHVOff():
             if (self.HV==False):
                 "variable para indicar en la db el fin del test y al programa"
                 self.startEndTest=True
                 self.isShutdown=True
                 
                 
                 if(self.status==2 and self.stopMarta==False):
                     
                     "marta funciona, hay que apagar lv y poner 20ºC"
                     stop()
                 else:

                     closeLVChannels()
                     self.timercheckDp_martaOff.timeout.connect(lambda:checkDP_shutdown())
                     self.timercheckDp_martaOff.start(self.TIME_DP_SHUTDOWN)

                     self.timerCheckMartaStatus.stop()
                     self.timerUpdateDewPointMarta.stop()
            
        def endTest_fullHeat():
            
                self.but_stopTest.setEnabled(False)

                print("dp superado")
                print("-------MARTA HEATING + LV ON-------")
                self.l_test_info.setText("FULL HEAT STOPPING PROCESS......")
                self.l_test_info2.setText("MARTA HEATING + LV ON......")
                self.marta.setTemperature(self.T_EMERGENCY_SHUTDOWN)
                self.startEndTest=True
                self.emergency=0
                stopHVtimer()
                stopEndTestTimer()
                hvStatus=self.arduino.getStatusHv()
                if (self.HV==True or hvStatus=="starting"):
                    orderArduino("OFF")
                else:
                    endTestEmergency()
                    
        def endTestEmergency():
                if (self.HV==False):
                    self.startEndTest=True
                    self.setLV=True
                    stopEndTestTimer()
                    stopHVtimer()
                     
                self.timercheckDpOff.timeout.connect(lambda:fullHeat_shutdown())
                self.timercheckDpOff.start(self.TIME_FULLHEAT)    
                    
        def emergencyStopProcess():
                print("-------APAGADO DE EMERGENCIA-------")
                self.l_test_info.setText("EMERGENCY STOPPING PROCESS......")
                self.l_test_info2.setText("")
                self.but_stopTest.setEnabled(False)
                stopEndTestTimer()
                stopHVtimer()
            
                if (self.HV==True and self.arduinoDead==False):
                    self.emergency=1
                    orderArduino("OFF")
                elif(self.HV==True and self.arduinoDead==True):
                    self.l_test_info2.setText("Stop CAEN MANUALLY ARDUINO CONN LOST")
                    self.l_test_info.setText("HEATING TO 15ºC")
                    self.marta.setTemperature(self.TEST_TEMPERATURE_HOT)
                    self.timerCheckArduino.stop()
                    emergencyShutDown()
                elif(self.HV==False and self.arduinoDead==False):
                    self.l_test_info2.setText("LV CONN LOST")
                    emergencyShutDown()
                else:
                    if(self.lvConLost==False and self.arduinoDead==False):
                     closeLVChannels()
                    emergencyShutDown()
                    
        def emergencyShutDown():
                    
                self.startEndTest=True
                stopEndTestTimer()
                stopHVtimer()
                self.marta.setTemperature(self.T_EMERGENCY_SHUTDOWN)
                print("----------CALENTANDO-----------")
                self.l_test_info2.setText("HEATING......")
                     
                self.timercheckEmergency.timeout.connect(lambda:checkEmergency_shutdown())
                self.timercheckEmergency.start(self.TIME_EMERGENCY_SHUTDOWN)   
                
        def resetLV():
            
            if(self.HV==False):
             self.mtti.turn_off(1)
             self.mtti.turn_off(2)
             self.mtti.turn_off(3)
            
             time=datetime.datetime.now()
             actualTime=time
            
             while((actualTime-time).total_seconds()<2):
              actualTime=datetime.datetime.now()
            
             self.mtti.turn_on(1)
             self.mtti.turn_on(2)
             self.mtti.turn_on(3)
            else:
                print("HV is ON")
                self.l_test_info2.setText("HV ON......")
            
        def itsdaqOn_Off():
            if(self.mtti.is_output_on(3)==1):
                self.mtti.turn_off(3)
                self.DAQ_on=False
            else:
                self.mtti.turn_on(3)
                self.DAQ_on=True             
                
       
         
        #acciones de lso botones
             
        self.but_connectMarta.clicked.connect(connectMarta)
        self.but_tempSetPoint.clicked.connect(setSetpoint)
        self.but_startTest.clicked.connect(startTest)
        self.but_stopTest.clicked.connect(endTest)
        self.but_abort_marta.clicked.connect(butUser_HVOff)
        self.but_manualTest.clicked.connect(startITSDAQTest)
        self.but_options.clicked.connect(openSettings)
        self.but_hvReady.clicked.connect(sendITSDAQorder)
        self.but_resetLv.clicked.connect(resetLV)
        self.but_itsdaqOn_Off.clicked.connect(itsdaqOn_Off)

        

        
        
    

if __name__ == "__main__":
    app=QtWidgets.QApplication(sys.argv)
    window=MainWindow()
    window.show()
    sys.exit(app.exec())

