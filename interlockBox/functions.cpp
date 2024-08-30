#include "functions.h"
#include <Arduino.h>

void printUint16Hex(uint16_t value) {
	Serial.print(value < 4096 ? "0" : "");
	Serial.print(value < 256 ? "0" : "");
	Serial.print(value < 16 ? "0" : "");
	Serial.print(value, HEX);
}

void printSerialNumber(uint16_t serial0, uint16_t serial1, uint16_t serial2) {
	Serial.print("Serial: 0x");
	printUint16Hex(serial0);
	printUint16Hex(serial1);
	printUint16Hex(serial2);
	Serial.println();
}

bool read_CO2(SensirionI2CScd4x scd4x) {
	uint16_t error;
	char errorMessage[256];
	// Read Measurement scd4x
	uint16_t co2;
	float temperature;
	float humidity;
	error = scd4x.readMeasurement(co2, temperature, humidity);
	if (error) {
		Serial.print("Error trying to execute readMeasurement(): ");
		errorToString(error, errorMessage, 256);
		Serial.println(errorMessage);
		return false;
	} else if (co2 == 0) {
		Serial.println("Invalid sample detected, skipping.");
		return false;
	} else {
		Serial.print("Co2:");
		Serial.print(co2);
		Serial.print("\t");
		Serial.print("Temperature:");
		Serial.print(temperature * 175.0 / 65536.0 - 45.0);
		Serial.print("\t");
		Serial.print("Humidity:");
		Serial.println(humidity * 100.0 / 65536.0);
	}
	return true;
}

void set_CO2(SensirionI2CScd4x scd4x) {
	uint16_t error;
	char errorMessage[256];

	scd4x.begin(Wire);

	// stop potentially previously started measurement
	error = scd4x.stopPeriodicMeasurement();
	if (error) {
		Serial.print("Error trying to execute stopPeriodicMeasurement(): ");
		errorToString(error, errorMessage, 256);
		Serial.println(errorMessage);
	}

	uint16_t serial0;
	uint16_t serial1;
	uint16_t serial2;
	error = scd4x.getSerialNumber(serial0, serial1, serial2);
	if (error) {
		Serial.print("Error trying to execute getSerialNumber(): ");
		errorToString(error, errorMessage, 256);
		Serial.println(errorMessage);
	} else {
		printSerialNumber(serial0, serial1, serial2);
	}

	// Start Measurement
	error = scd4x.startPeriodicMeasurement();
	if (error) {
		Serial.print("Error trying to execute startPeriodicMeasurement(): ");
		errorToString(error, errorMessage, 256);
		Serial.println(errorMessage);
	}
}

void setDigitalPins(int* gpio){ // Set the default function (I/O) for the digital pins
  pinMode(gpio[0], INPUT); // GPIO_1
  pinMode(gpio[1], INPUT); // GPIO_2
  pinMode(gpio[2], INPUT); // GPIO_3
  pinMode(HV_INTLK, OUTPUT); // GPIO_4 used for HV interlock (modified on-board resistor to match optocoupler current)
  pinMode(RELAY4, OUTPUT);

  digitalWrite(HV_INTLK, HIGH); // GPIO_2
  digitalWrite(RELAY4, LOW);
}

bool I2C_SW(byte cn, bool testoutput) {
	char msg[128] = { '\0' };
	uint8_t nErrors = 0;
	byte addr = 250;

	// Retry up to 3 times if the channel doesn't switch properly
	for (uint8_t i = 0; i < 3; i++) {
		Wire.begin();
		Wire.setTimeout(1000);
		Wire.beginTransmission(SW_ADDRS);
		Wire.write(channel[cn]);
		byte error = Wire.endTransmission();
		delay(10);
		// Check switched correct address
		Wire.requestFrom(SW_ADDRS, 1);
		addr = Wire.read();
		error = error + Wire.endTransmission();
		error = error + addr;
		if(testoutput){
      if (error != channel[cn]) {
        snprintf(msg, sizeof(msg), "\tError switching I2C: %X (%X)", cn,
            error);
      } else {
        Serial.print("\tSwitched I2C to channel: ");
        Serial.println(cn);
        return true;
      }
    }
	}
	return false;
}

void readHYT939(float *Temp, float *RH, float *DewPoint) {
	int Addr = 0x28;
  //	int Addr = 0x11;
	unsigned int data[4];
  // Start I2C Transmission
	Wire.beginTransmission(Addr);
  // Send normal mode command
	Wire.write(0x80);
  // Stop I2C transmission
	Wire.endTransmission();
	delay(300);
  // Request 4 bytes of data
	Wire.requestFrom(Addr, 4);

  // Read 4 bytes of data
  // humidity msb, humidity lsb, temp msb, temp lsb
	if (Wire.available() == 4) {
		data[0] = Wire.read();
		data[1] = Wire.read();
		data[2] = Wire.read();
		data[3] = Wire.read();

  // Convert the data to 14-bits
		*RH = (((data[0] & 0x3F) * 256.0) + data[1]) * (100.0 / 16383.0);
		*Temp = (((data[2] * 256.0) + (data[3] & 0xFC)) / 4) * (165.0 / 16383.0) - 40;
  //		*DewPoint = *Temp - ((100 - *RH) / 5.);
		float a = 6.1121;
		float b = 17.368;
		float c = 238.88;
		float d = 234.5;
    float GammaM = 0.;
    if(*RH>=0.01) GammaM = log(*RH / 100 * exp((b - *Temp / d) * (*Temp / (c + *Temp))));
    else  GammaM = log(0.01 / 100 * exp((b - *Temp / d) * (*Temp / (c + *Temp))));
    *DewPoint = (c * GammaM) / (b - GammaM);
	} else {
		*RH = NAN;
		*Temp = NAN;
		*DewPoint = NAN;
	}
}

float readNTC(byte n, bool testoutput = false) {
	analogReadResolution(12);
	int Rc = 15e3; //valor de la resistencia
	int Rd1 = 62e3; // Resistor divider 1
	int Rd2 = 100e3; // Resistor divider 2
	int Rx = Rd1 + Rd2;
  //	float Vcc = Vint[A_5V_ID].getValue();
	float Vcc = 3.3;
  /* 
	// Vishai NTCALUG02A103F parameters 0;25;55�C
	float A = 1.138890870e-3;
	float B = 2.325501268e-4;
	float C = 0.9376448112e-7;
	float K = 10; //factor de disipacion en mW/C

	//	NTC TDK parameters
	float A = 1.122980887e-3;
	float B = 2.350616989e-4;
	float C = 0.8452478720e-7;
	float K = 3; //factor de disipacion en mW/C
  */
	//	 NTC on EoS --> 103KT1608T-1P parameters -40;0;50
		float A = 0.7642759641e-3;
		float B = 2.745848936e-4;
		float C = 0.7755606923e-7;
		float K = 0.9; //factor de disipacion en mW/C

	float AnalogPins[] = ANALOG_PINS;
	float V = analogRead(AnalogPins[n]) * VOLTS;
  /* 
  // Resistive divider
	float R = (Rc * V) / (Vcc - V);
	float R = (Rc * V) / (Vcc - V) * 2 RD - Rc * V; //Add dissipation heat

  // Two concatenated resistive dividers
	float R = (V * Rc * Rx) / (Vcc * Rx - V * Rx - Rc * V);
  */
  // Freaky measure, voltage divider with 100k resistor in parallel with NTC
	float R100k = 100e3;
	float Rparallel = (Rc * V) / (Vcc - V);
	float R = (R100k * Rparallel) / (R100k - Rparallel);
	if(testoutput){
    Serial.print("Measured Parallel resistor: ");
    Serial.print(Rparallel);
    Serial.print(" --> Calculated NTC: ");
    Serial.print(R);
  }
	float logR = log(R);
	float R_th = 1.0 / (A + B * logR + C * logR * logR * logR);

  //	float kelvin = R_th - V * V / (K * R) * 1000;
	float kelvin = R_th;
	float celsius = kelvin - 273.15;
  if(testoutput){
    Serial.print("  --> ");
    Serial.print(celsius);
    Serial.println("°C");
  }
  return celsius;
}

float readFlow(int n){
  analogReadResolution(12);
  float Vflow = analogRead(n) * VOLTS; // ADC maximum voltage is 3.3V, flow meter range 0-10V or 1-5V or 4-20mA
  float outflow = ( ( Vflow - LOWSIG_FLOW ) / ( HISIG_FLOW - LOWSIG_FLOW ) ) * ( MAX_FLOW - MIN_FLOW ) + MIN_FLOW;
  return outflow;
}

void setupWiFi(const char* ssid, int status, byte* mac, bool testoutput = false){
  if(testoutput){
    Serial.println("Scanning available networks...");
    scanNetworks();
  }
  int loop = 0;
  while (status != WL_CONNECTED) {
    if(loop>4){
      if(testoutput){
        Serial.print("Connection to ");
        Serial.print(ssid);
        Serial.println(" failed");
      }
      break;
    }
    if(testoutput){
      Serial.print("Attempting to connect to network: ");
      Serial.println(ssid);
    }
    status = WiFi.begin(ssid);
    //status = WiFi.begin(ssid, pass) //suitable for WPA network
    // wait 5 seconds for connection:
    delay(5000);
    loop++;
  }

  //printing MAC address
  WiFi.macAddress(mac);
  if(testoutput){
    Serial.print("MAC address: ");
    Serial.print(mac[5],HEX);
    Serial.print(":");
    Serial.print(mac[4],HEX);
    Serial.print(":");
    Serial.print(mac[3],HEX);
    Serial.print(":");
    Serial.print(mac[2],HEX);
    Serial.print(":");
    Serial.print(mac[1],HEX);
    Serial.print(":");
    Serial.println(mac[0],HEX);
  
    // you're connected now, so print out the data:
    Serial.println("You're connected to the network");

    Serial.println("----------------------------------------");
    printWiFiData();
    Serial.println("----------------------------------------");
  }
}

void scanNetworks() {
  // scan for nearby networks:
  Serial.println("** Scan Networks **");
  byte numSsid = WiFi.scanNetworks();

  // print the list of networks seen:
  Serial.print("SSID List:");
  Serial.println(numSsid);
  // print the network number and name for each network found:
  for (int thisNet = 0; thisNet<numSsid; thisNet++) {
    Serial.print(thisNet);
    Serial.print(") Network: ");
    Serial.println(WiFi.SSID(thisNet));
  }
}

void printWiFiData() {
  Serial.println("Board Information:");
  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  Serial.println();
  Serial.println("Network Information:");
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.println(rssi);

}

void sendDataDB(float* Temp, float* RH, float* DewPoint,const int nHYT,const int nNTC, float flow, bool hv_intlk = false, bool hv_signal = false){
  Serial.flush();
  Serial.println("###### Sending data to PC ######");
  char msgDB[128];
  snprintf(msgDB,sizeof(msgDB),"nHYT:  %d     nNTC:  %d",nHYT,nNTC);
  Serial.println(msgDB);
  Serial.print("Temp:  ");
  for(int i = 0; i < nHYT + nNTC; i++){
    Serial.print(Temp[i]);
    Serial.print("  ");
  }
  Serial.println();
  Serial.print("RH:  ");
  for(int i = 0; i < nHYT; i++){
    Serial.print(RH[i]);
    Serial.print("  ");
  }
  Serial.println();
  Serial.print("DewPoint:  ");
  for(int i = 0; i < nHYT; i++){
    Serial.print(DewPoint[i]);
    Serial.print("  ");
  }
  Serial.println();
  Serial.print("Flow:  ");
  Serial.println(flow);
  Serial.print("HV_Intlk:  ");
  Serial.println(hv_intlk);
  Serial.print("HV_ON:  ");
  Serial.println(hv_signal);
  //Serial.println("****** End of sending data ******");
}

bool condition_door(int* gpio, const int nHYT, const int nNTC, float* temp, float* rh, float* dew, bool testmode){
  bool opendoor = true;
  //Check cooling off by looking to NTC temperature
  for(int i = 0; i < nNTC; i++){
    if(temp[nHYT + i] < 17) opendoor = false;
  }
  //Check DewPoint lower than room temperature (around 20C)
  for(int i = 0; i < nHYT; i++){
    if(!(1.2 * dew[nHYT] < 20.)) opendoor = false;
  }
  //Check if HV_Signal is ON (still to decide correct pin)
  bool hvsig = digitalRead(gpio[0]);
  opendoor = opendoor && hvsig;
  return opendoor;
}