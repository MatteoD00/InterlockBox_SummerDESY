/*
 * Copyright (c) 2021, Sensirion AG
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * * Redistributions of source code must retain the above copyright notice, this
 *   list of conditions and the following disclaimer.
 *
 * * Redistributions in binary form must reproduce the above copyright notice,
 *   this list of conditions and the following disclaimer in the documentation
 *   and/or other materials provided with the distribution.
 *
 * * Neither the name of Sensirion AG nor the names of its
 *   contributors may be used to endorse or promote products derived from
 *   this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

#include <Arduino.h>
#include <Wire.h>
#include "arduino_secrets.h" //must be created to store WiFi credentials
#include "config_io.h" // define configuration of pins and other parameters
#include "functions.h"

//define variable for counting loops
int nloop;
//define variables for WiFi settings
const char ssid[] = SECRET_SSID;
const char user[] = SECRET_USER;
const char pass[] = SECRET_PASS;
int status = WL_IDLE_STATUS; 
byte mac[6];
//define number of sensors connected
const int nHYT = 2;
const int nNTC = 2;
const int nGPIO = 4;
const bool boolFlow = true;
const int pinFlow = 4;

int gpio[] = GPIO_PINS;
SensirionI2CScd4x scd4x;
Adafruit_SHT31 SHTxx;

void setup() {
	Serial.begin(115200);
	while (!Serial) {
		delay(100);
  }
  Serial.println("\n\nRestart Arduino");
  setDigitalPins(gpio);
  setupWiFi(ssid, status, mac);

  nloop = 0;
	pinMode(SENS_PW, OUTPUT);

	Wire.begin();
	//set_CO2(); //No scd4x sensors used
	//SHTxx.begin(DEFAULT_SHTXX_ADDRS); //no SHT sensors used
}

void loop() {
  char msg[128] = { NULL };
  snprintf(msg, sizeof(msg),"\nStart of loop n.%d",nloop);
  Serial.println(msg);
	// Switching on Digital sensors
	digitalWrite(SENS_PW, LOW);
	delay(100);
	float Temp = NAN;
	float RH = NAN;
	float DewPoint = NAN;
  bool intlkHYT = false;
  for (int ch = 0; ch < nHYT; ch++) {   // "<= CHANNEL_NUM" default end condition
    //Change channel
    I2C_SW(ch);
    // read_CO2();
    // HYT939
    readHYT939(&Temp, &RH, &DewPoint);
    snprintf(msg, sizeof(msg), "Sensor_%u_HYT939 ", ch);
    Serial.print(msg);
    snprintf(msg, sizeof(msg), " --> Temp: %0.2f; RH: %0.2f; DP: %0.2f", Temp, RH, DewPoint);
    Serial.println(msg);
    if(Temp>25. || RH>50. || DewPoint>Temp){
      intlkHYT = true;
      // issueHYT() --> implementing function for issue related to HYT monitoring
    }
    
  /*
    // SHT35 (not used @DESY at the moment)
    Temp = SHTxx.readTemperature();
    RH = SHTxx.readHumidity();
    snprintf(msg, sizeof(msg), "Sensor_%u_SHT35", ch);
    Serial.print(msg);
    snprintf(msg, sizeof(msg), " --> Temp: %0.2f; RH: %0.2f; DP: %0.2f", Temp, RH, DewPoint);
    Serial.println(msg);
  */
  }
  bool intlkNTC = false;
	for (int ch = 0; ch < nNTC; ch++) {
    Temp = readNTC(ch);
    /*
		snprintf(msg, sizeof(msg), "NTC_%d", ch);
		snprintf(msg, sizeof(msg), " --> NTC_Temp: %0.2f", Temp);
    */
    if(Temp>17.){
      intlkNTC = true;
      // issueNTC() --> implement function for issues on petal temperature
    }
	}
  bool intlkFlow = false;
  if(boolFlow){
    float flow = readFlow(4);
    snprintf(msg,sizeof(msg),"Current airflow is: %.2f l/min",flow);
    Serial.println(msg);
    if(flow<1.){
      intlkFlow = true;
      //issueFlow() --> implement function if airflow too low
    }
  }
  bool intlkHV = digitalRead(gpio[1]);
  // if may contain a function for HV related issues
  if(intlkHV){
    digitalWrite(gpio[3], HIGH);
    digitalWrite(RELAY4, LOW);
  }
  else{
    digitalWrite(gpio[3], LOW);
    digitalWrite(RELAY4, HIGH);
  }
  
  // Read GPIO connections
  for(int i = 0; i < nGPIO; i++){
    bool dout = digitalRead(gpio[i]);
    snprintf(msg, sizeof(msg), "GPIO_%d state: %s", i+1, dout ? "true" : "false");
    Serial.println(msg);
  }
  bool dout = digitalRead(RELAY4);
  snprintf(msg, sizeof(msg), "Relay_4 state: %s", dout ? "Closed" : "Open");
  Serial.println(msg);

  // Switching off Digital sensors
  digitalWrite(SENS_PW, HIGH);
  
  snprintf(msg,sizeof(msg),"End of loop n.%d",nloop);
  Serial.println(msg);
  
  nloop++;
	delay(2000);
}