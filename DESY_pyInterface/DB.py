# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 10:10:38 2023

@author: oielsu
"""

from influxdb_client import InfluxDBClient
import influxdb_client as dbc
from influxdb_client.client.write_api import SYNCHRONOUS

class DB:
    
 """
 fill the data and check where do you want to upload your data
 """
    
 ip=""
 port=8086
 org=""
 username=""
 password=""
 
 
 "petalbox"
 token=""
 
 bucket=""



 def logging(self):
     try:
      self.client=InfluxDBClient(url=self.ip, token=self.token, org=self.org)
     except:
         print("itkendcap4 error")
     
 def logout(self):
     try:
      self.client.close()
     except:
          print("itkendcap4 error")
     
 def writeQuary(self):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
  
      point =dbc.Point("pruebas2").tag("Test", "petal_test_pruebas").field("Test_On", True)
      write_api.write(bucket=self.bucket, org=self.org, record=point)
     except:
          print("itkendcap4 error")

 def testOff(self):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
  
      point =dbc.Point("pruebas2").tag("Test", "petal_test_pruebas").field("Test_On", False)
      write_api.write(bucket=self.bucket, org=self.org, record=point)
     except:
         print("itkendcap4 error")
         
 def updateMartaValues(self,values):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
   
      for key, value  in values.items():
       point =dbc.Point("pruebas2").tag("Test", "petal_test_pruebas").field(key, value)
       write_api.write(bucket=self.bucket, org=self.org, record=point)
     except:
         print("itkendcap4 error")
         
 def setMARTAstatus(self,status):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
     
      point = dbc.Point("COMM").tag("SETUP", self.org).tag("SENDER","PETALBOX").tag("RECEIVER","ANY").field("MARTA_STATUS",status)
      write_api.write(bucket=self.bucket, org=self.org, record=point) 
     except:
         print("itkendcap4 error")

 def updateMARTAsp(self,sp):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
     
      point = dbc.Point("COMM").tag("SETUP", self.org).tag("SENDER","PETALBOX").tag("RECEIVER","ANY").field("MARTA_SP","SP: "+str(sp))
      write_api.write(bucket=self.bucket, org=self.org, record=point) 
     except:
         print("itkendcap4 error")
         
 def updateArduinoValues(self,values):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
    
      for key, value  in values.items():
          try:
            point =dbc.Point("pruebas2").tag("Test", "petal_test_pruebas").field(key, float(value))
            write_api.write(bucket=self.bucket, org=self.org, record=point)
          except:
           if(value=="ON"):
               value=float(True)
           elif(value=="OFF"):
               value=float(False)
           if(value!="starting" and value!="stopping"):
            point =dbc.Point("pruebas2").tag("Test", "petal_test_pruebas").field(key, value)
            write_api.write(bucket=self.bucket, org=self.org, record=point)
     except:
         print("itkendcap4 error")
         
 def updateVoltages(self,values):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
   
      for key, value  in values.items():
       point =dbc.Point("pruebas2").tag("Test", "petal_test_pruebas").field(key, value)
       write_api.write(bucket=self.bucket, org=self.org, record=point)
     except:
         print("itkendcap4 error")
         
 def writeError(self,error):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
     
      point = dbc.Point("COMM").tag("SETUP", self.org).tag("SENDER","PETALBOX").tag("RECEIVER","ANY").field("ERROR",error)
      write_api.write(bucket=self.bucket, org=self.org, record=point) 
     except:
         print("itkendcap4 error")
         
 def setColdCharacterization(self):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
     
      point = dbc.Point("COMM").tag("SETUP", self.org).tag("SENDER","PETALBOX").tag("RECEIVER","ITSDAQ").field("COMMAND","RUN_COLD_CHARACTERISATION").field("DATA","{'modules':[]}").field("ERROR", "NONE")
      write_api.write(bucket=self.bucket, org=self.org, record=point) 
     except:
         print("itkendcap4 error")
         
 def setWarmCharacterization(self):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
     
      point = dbc.Point("COMM").tag("SETUP", self.org).tag("SENDER","PETALBOX").tag("RECEIVER","ITSDAQ").field("COMMAND","RUN_WARM_CHARACTERISATION").field("DATA","{'modules':[]}").field("ERROR", "NONE")
      write_api.write(bucket=self.bucket, org=self.org, record=point) 
     except:
         print("itkendcap4 error")
         
 def setWarmCharacterizationColdjig(self):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
     
      point = dbc.Point("COMM").tag("SETUP", self.org).tag("SENDER","COLDJIG").tag("RECEIVER","ITSDAQ").field("COMMAND","RUN_WARM_CHARACTERISATION").field("DATA","{'modules':[]}").field("ERROR", "NONE")
      write_api.write(bucket="coldjig", org=self.org, record=point) 
     except:
         print("itkendcap4 error")
         
 def initModules(self):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
     
      point = dbc.Point("COMM").tag("SETUP", self.org).tag("SENDER","PETALBOX").tag("RECEIVER","ITSDAQ").field("COMMAND","INIT_MODULES").field("DATA","{'modules':[]}").field("ERROR", "NONE")
      write_api.write(bucket=self.bucket, org=self.org, record=point)
     except:
         print("itkendcap4 error")
         
 def initModulesColdjig(self):
     try:
      write_api = self.client.write_api(write_options=SYNCHRONOUS)
     
      point = dbc.Point("COMM").tag("SETUP", self.org).tag("SENDER","COLDJIG").tag("RECEIVER","ITSDAQ").field("COMMAND","INIT_MODULES").field("DATA","{'modules':[]}").field("ERROR", "NONE")
      write_api.write(bucket="coldjig", org=self.org, record=point)
     except:
         print("itkendcap4 error")
         
 def readQuery(self,query):
     try:
      return self.client.query_api().query(query, org=self.org)
     except:
         print("itkendcap4 error")

 def getStarted(self):
     query=f""" from(bucket: "{self.bucket}")
  |> range(start:-5m)
  |> filter(fn: (r) => r["_measurement"] == "COMM")
  |> filter(fn: (r) => r["RECEIVER"] == "PETALBOX")
  |> filter(fn: (r) => r["SENDER"] == "ITSDAQ")
  |> filter(fn: (r) => r["_field"] == "DATA")
  |> sort(columns: ["_time"], desc: true)"""
     result=self.readQuery(query)
     try:
         if(result[0].records[0].get_value()=="Starting"):
           isStarted = True
         else:
           isStarted = False  
     except:
         isStarted=None
     return isStarted
 
 def getStartedColdjig(self):
     query=f""" from(bucket: "coldjig")
  |> range(start:-30m)
  |> filter(fn: (r) => r["_measurement"] == "COMM")
  |> filter(fn: (r) => r["RECEIVER"] == "COLDJIG")
  |> filter(fn: (r) => r["SENDER"] == "ISTDAQ")
  |> filter(fn: (r) => r["SETUP"] == "IFIC")
  |> filter(fn: (r) => r["_field"] == "DATA")
  |> sort(columns: ["_time"], desc: true)"""
     result=self.readQuery(query)
     try:
         if(result[0].records[0].get_value()=="Complete"):
           isStarted = True
         else:
           isStarted = False  
     except:
         isStarted=None
     return isStarted
 
 def getCompleted(self):
     query=f"""from(bucket: "{self.bucket}")
  |> range(start:-5m)
  |> filter(fn: (r) => r["_measurement"] == "COMM")
  |> filter(fn: (r) => r["RECEIVER"] == "PETALBOX")
  |> filter(fn: (r) => r["SENDER"] == "ITSDAQ")
  |> filter(fn: (r) => r["_field"] == "DATA")
  |> sort(columns: ["_time"], desc: true)"""
     result=self.readQuery(query)
     try:
         if(result[0].records[0].get_value()=="Complete"):
           isCompleted = True
         else:
           isCompleted = False  
     except:
         isCompleted=None
     return isCompleted
 
 def getReady(self):
     query=f"""from(bucket: "{self.bucket}")
  |> range(start:-5h)
  |> filter(fn: (r) => r["_measurement"] == "COMM")
  |> filter(fn: (r) => r["RECEIVER"] == "ANY")
  |> filter(fn: (r) => r["SENDER"] == "ITSDAQ")
  |> filter(fn: (r) => r["SETUP"] == "IFIC")
  |> filter(fn: (r) => r["_field"] == "DATA")
  |> sort(columns: ["_time"], desc: true)"""
     result=self.readQuery(query)
     try:
         if(result[0].records[0].get_value()=="READY"):
           isReady = True
         else:
           isReady = False  
     except:
         isReady=None
     return isReady

"""
a=DB()
a.logging()
#b=a.initModulesColdjig()
#b=a.setWarmCharacterizationColdjig()
#a=a.getStartedColdjig()
#c=a.setWarmCharacterization()
q=a.getStarted()
v=a.getCompleted()
#a.logout()

"""






