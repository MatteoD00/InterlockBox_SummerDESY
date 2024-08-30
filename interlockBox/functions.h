#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include <Arduino.h>
#include <SensirionI2CScd4x.h> // Not used in DESY setup
#include <Wire.h>
#include <Adafruit_SHT31.h> // Not used in DESY setup
#include <WiFiNINA.h>
#include "arduino_secrets.h" //must be created to store WiFi credentials
#include "config_io.h" // define configuration of pins and other parameters
/*
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
const byte channel[CHANNEL_NUM] PROGMEM = { 0b0001, 0b0010, 0b0100, 0b1000 };
*/
const byte channel[CHANNEL_NUM] PROGMEM = { 0b0001, 0b0010, 0b0100, 0b1000 };

void printUint16Hex(uint16_t value);
void printSerialNumber(uint16_t serial0, uint16_t serial1, uint16_t serial2);
bool read_CO2(SensirionI2CScd4x scd4x);
void set_CO2(SensirionI2CScd4x scd4x);
void setDigitalPins(int* gpio);
bool I2C_SW(byte cn,bool testoutput);
void readHYT939(float *Temp, float *RH, float *DewPoint);
float readNTC(byte n, bool testoutput);
float readFlow(int n);
void setupWiFi(const char* ssid, int status, byte* mac, bool testoutput);
void scanNetworks();
void printWiFiData();
void sendDataDB(float* Temp, float* RH, float* DewPoint, const int nHYT, const int nNTC, float flow, bool hv_intlk, bool hv_signal);
bool condition_door(int* gpio, const int nHYT, const int nNTC, float* temp, float* rh, float* dew, bool testmode = false);

#endif