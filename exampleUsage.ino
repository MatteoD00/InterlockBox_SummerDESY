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
#include <SensirionI2CScd4x.h>
#include <Wire.h>
#include <Adafruit_SHT31.h>

# define SENS_PW 13	 // P-MOSFET activating I2C sensors power
#define RELAY1			A5
#define RELAY2			A6
#define RELAY3			0
#define RELAY4			1
#define ANALOG_PINS { 2, 3, 4 }
#define AnalogResolution 12  //10 bits
#define ADCvolts 3.3
#define ADCsteps 4095 // 12 bits
//#define ADCsteps 1023 // 10 bits
#define VOLTS	(ADCvolts/ADCsteps)

SensirionI2CScd4x scd4x;
// I2C switch address
#define SW_ADDRS 		0x70	//0x70 to 0x77 depending on address pins
#define CHANNEL_NUM	5
const byte channel[CHANNEL_NUM] PROGMEM = { 0b0000, 0b0001, 0b0010, 0b0100,
		0b1000 };

#define DEFAULT_SHTXX_ADDRS 0x44

Adafruit_SHT31 SHTxx;

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

bool read_CO2() {
	uint16_t error;
	char errorMessage[256];
	// Read Measurement scd4x
	uint16_t co2;
	uint16_t temperature;
	uint16_t humidity;
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
void set_CO2() {
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

void setup() {

	Serial.begin(115200);
	while (!Serial) {
		delay(100);
	}

	pinMode(SENS_PW, OUTPUT);

	Wire.begin();
	set_CO2();
	SHTxx.begin(DEFAULT_SHTXX_ADDRS);
}

void loop() {
	// Switching on Digital sensors
	digitalWrite(SENS_PW, LOW);
	delay(100);
	char msg[128] = { NULL };
	float Temp = NAN;
	float RH = NAN;
	float DewPoint = NAN;

	for (int ch = 0; ch <= CHANNEL_NUM; ch++) {
		//Change channel
		I2C_SW(ch);
//		read_CO2();
		// HYT939
		readHYT939(&Temp, &RH, &DewPoint);
		snprintf(msg, sizeof(msg), "Sensor_%u_HYT939 ", ch);
		Serial.print(msg);
		snprintf(msg, sizeof(msg), " --> Temp: %0.2f; RH: %0.2f; DP: %0.2f",
				msg, Temp, RH, DewPoint);
		Serial.println(msg);
		// SHT35
		Temp = SHTxx.readTemperature();
		RH = SHTxx.readHumidity();
		snprintf(msg, sizeof(msg), "Sensor_%u_SHT35", ch);
		Serial.print(msg);
		snprintf(msg, sizeof(msg), " --> Temp: %0.2f; RH: %0.2f; DP: %0.2f",
		msg, Temp, RH, DewPoint);
		Serial.println(msg);
	}

	// Switching off Digital sensors
		digitalWrite(SENS_PW, HIGH);
		delay(100);

	for (int ch = 0; ch <= 2; ch++) {
		Temp = readNTC(ch);
		snprintf(msg, sizeof(msg), "NTC_%d", ch);
		snprintf(msg, sizeof(msg), " --> NTC_Temp: %0.2f",msg, Temp);
	}

	delay(5000);
}

bool I2C_SW(byte cn) {
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
		if (error != channel[cn]) {
			snprintf(msg, sizeof(msg), "\tError switching I2C: %X (%X)", cn,
					error);
		} else {
			Serial.print("\Switched I2C to channel: ");
			Serial.println(cn);
			return true;
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
		*Temp = (((data[2] * 256.0) + (data[3] & 0xFC)) / 4) * (165.0 / 16383.0)
				- 40;
//		*DewPoint = *Temp - ((100 - *RH) / 5.);
		float a = 6.1121;
		float b = 17.368;
		float c = 238.88;
		float d = 234.5;
		float GammaM = log(
				*RH / 100 * exp((b - *Temp / d) * (*Temp / (c + *Temp))));
		*DewPoint = (c * GammaM) / (b - GammaM);
	} else {
		*RH = NAN;
		*Temp = NAN;
		*DewPoint = NAN;
	}
}

float readNTC(byte n) {
	analogReadResolution(12);
	int Rc = 15e3; //valor de la resistencia
	int Rd1 = 62e3; // Resistor divider 1
	int Rd2 = 100e3; // Resistor divider 2
	int Rx = Rd1 + Rd2;
//	float Vcc = Vint[A_5V_ID].getValue();
	float Vcc = 3.3;

////	Vishai NTCALUG02A103F parameters 0;25;55ºC
//	float A = 1.138890870e-3;
//	float B = 2.325501268e-4;
//	float C = 0.9376448112e-7;
//	float K = 10; //factor de disipacion en mW/C

//	//	NTC TDK parameters
//	float A = 1.122980887e-3;
//	float B = 2.350616989e-4;
//	float C = 0.8452478720e-7;
//	float K = 3; //factor de disipacion en mW/C

	//	 NTC on EoS --> 103KT1608T-1P parameters -40;0;50
		float A = 0.7642759641e-3;
		float B = 2.745848936e-4;
		float C = 0.7755606923e-7;
		float K = 0.9; //factor de disipacion en mW/C

	float AnalogPins[] = ANALOG_PINS;
	float V = analogRead(AnalogPins[n]) * VOLTS;

// Resistive divider
//	float R = (Rc * V) / (Vcc - V);
//	float R = (Rc * V) / (Vcc - V) * 2 RD - Rc * V; //Add dissipation heat

// Two concatenated resistive dividers
//	float R = (V * Rc * Rx) / (Vcc * Rx - V * Rx - Rc * V);

// Freaky measure, voltage divider with 100k resistor in parallel with NTC
	float R100k = 100e3;
	float Rparallel = (Rc * V) / (Vcc - V);
	float R = (R100k * Rparallel) / (R100k - Rparallel);
	Serial.print("Measured Parallel resistor: ");
	Serial.print(Rparallel);
	Serial.print(" --> Calculated NTC: ");
	Serial.print(R);

	float logR = log(R);
	float R_th = 1.0 / (A + B * logR + C * logR * logR * logR);

//	float kelvin = R_th - V * V / (K * R) * 1000;
	float kelvin = R_th;
	float celsius = kelvin - 273.15;
	Serial.print("  --> ");
	Serial.print(celsius);
	Serial.println("ºC");
	return celsius;
}
