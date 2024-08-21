# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 14:06:20 2023

@author: oielsu
"""

#from PyQt5 import uic,QtWidgets,QtCore 
from PyQt6 import uic,QtWidgets,QtCore
import sys
import bgImage

qtCreatorFile = "gui/SetingsWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class SettingsWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
    saveClicked= QtCore.pyqtSignal(dict)
    
    def __init__(self,params): 
        QtWidgets.QMainWindow.__init__(self) 
        Ui_MainWindow.__init__(self)
        self.setupUi(self) 
        self.params=params
        self.sp_tWarm.setValue(float(params["TEST_TEMPERATURE_HOT"]))
        self.sp_tCold.setValue(float(params["TEST_TEMPERATURE_COLD"]))
        self.sp_tShutdown.setValue(float(params["T_SHUTDOWN"]))
        self.sp_teos_max.setValue(float(params["T_EOS_MAX"]))
        self.sp_teos_min.setValue(float(params["T_EOS_LIMIT"]))
        self.sp_tsensor_max.setValue(float(params["SENSOR_LIMIT_SUP"]))
        self.sp_tsensor_min.setValue(float(params["SENSOR_LIMIT"]))
        self.sp_arduino.setValue(params["TIME_ARDUINO"]/1000)
        self.sp_status.setValue(params["TIME_MARTA"]/1000)
        self.sp_dp.setValue(params["TIME_DEWPOINT"]/1000)
        self.sp_lv.setValue(params["TIME_CHECK_LV"]/1000)
        self.sp_marta.setValue(params["TIME_MARTA_PARAMS"]/1000)
        self.sp_param_marta.setValue(params["TIME_PARAMS"]/1000)
        self.sp_endTest.setValue(params["TIME_CHECK_END_TEST"]/60000)
        self.sp_timeout.setValue(params["TIMEOUT"])
           
        def closeEvent(self, event):
            super(SettingsWindow, self).closeEvent(event)
        
        
        def updateValues():
         
           self.params["TEST_TEMPERATURE_HOT"]=self.sp_tWarm.value()
           self.params["TIME_ARDUINO"]=self.sp_arduino.value()*1000
           self.params["TEST_TEMPERATURE_COLD"]=self.sp_tCold.value()
           self.params["T_SHUTDOWN"]=self.sp_Shutdown.value()
           self.params["T_EOS_MAX"]=self.sp_teos_max.value()
           self.params["T_EOS_LIMIT"]=self.sp_teos_min.value()
           self.params["SENSOR_LIMIT_SUP"]=self.sp_tsensor_max.value()
           self.params["SENSOR_LIMIT"]=self.sp_tsensor_min.value()
           self.params["TIME_MARTA"]=self.sp_status.value()*1000
           self.params["TIME_DEWPOINT"]=self.sp_dp.value()*1000
           self.params["TIME_CHECK_LV"]=self.sp_lv.value()*1000
           self.params["TIME_MARTA_PARAMS"]=self.sp_marta.value()*1000
           self.params["TIME_PARAMS"]=self.sp_param_marta.value()*1000
           self.params["TIME_CHECK_END_TEST"]=self.sp_endTest.value()*60000
           self.params["TIMEOUT"]=self.sp_timeout.value()
           self.saveClicked.emit(self.params)
           self.close()

            
        #acciones de lso botones
             
        self.but_save.clicked.connect(updateValues)
        self.but_coldTest.enterEvent= lambda e: self.info.setText("Temperature to start cold test")
        self.but_coldTest.leaveEvent= lambda e: self.info.setText("")
        self.but_warmTest.enterEvent= lambda e: self.info.setText("Temperature to start warm test")
        self.but_warmTest.leaveEvent= lambda e: self.info.setText("")
        self.but_shutdown.enterEvent= lambda e: self.info.setText("Temperature to stop MARTA after LV OFF-HVOFF")
        self.but_shutdown.leaveEvent= lambda e: self.info.setText("")
        self.but_sensor_max.enterEvent= lambda e: self.info.setText("Temperature max to stablish a normal sensor behavior")
        self.but_sensor_max.leaveEvent= lambda e: self.info.setText("")
        self.but_sensor_min.enterEvent= lambda e: self.info.setText("Temperature min to stablish a normal sensor behavior")
        self.but_sensor_min.leaveEvent= lambda e: self.info.setText("")
        self.but_eos_max.enterEvent= lambda e: self.info.setText("Allowed max T for eos")
        self.but_eos_max.leaveEvent= lambda e: self.info.setText("")
        self.but_eos_min.enterEvent= lambda e: self.info.setText("Allowed min T for eos")
        self.but_eos_min.leaveEvent= lambda e: self.info.setText("")
        self.but_arduino.enterEvent= lambda e: self.info.setText("comunication time between App and Sentuino")
        self.but_arduino.leaveEvent= lambda e: self.info.setText("")
        self.but_dp.enterEvent= lambda e: self.info.setText("time for check initial DP conditions before starting MARTA")
        self.but_dp.leaveEvent= lambda e: self.info.setText("")
        self.but_lv.enterEvent= lambda e: self.info.setText("time for check lv conditions")
        self.but_lv.leaveEvent= lambda e: self.info.setText("")
        self.but_marta.enterEvent= lambda e: self.info.setText("time to check marta DP and P")
        self.but_marta.leaveEvent= lambda e: self.info.setText("")
        self.but_status.enterEvent= lambda e: self.info.setText("time to check MARTA status (on,co2 working,alarm)")
        self.but_status.leaveEvent= lambda e: self.info.setText("")
        self.but_timeout.enterEvent= lambda e: self.info.setText("timeout for itsdaq")
        self.but_timeout.leaveEvent= lambda e: self.info.setText("")
        self.but_endTest.enterEvent= lambda e: self.info.setText("time for check end test from itsdaq")
        self.but_endTest.leaveEvent= lambda e: self.info.setText("")
        "repetir para resto botones"

        
        
    

if __name__ == "__main__":
    app=QtWidgets.QApplication(sys.argv)
    window=SettingsWindow()
    window.show()
    #para pyqt5 y descomentar el import claro
    #sys.exit(app.exec_())
    sys.exit(app.exec())

