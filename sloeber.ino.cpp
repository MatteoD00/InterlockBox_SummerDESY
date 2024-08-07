#ifdef __IN_ECLIPSE__
//This is a automatic generated file
//Please do not modify this file
//If you touch this file your change will be overwritten during the next build
//This file has been generated on 2024-08-07 13:27:59

#include "Arduino.h"
#include <Arduino.h>
#include <SensirionI2CScd4x.h>
#include <Wire.h>
#include <Adafruit_SHT31.h>

void printUint16Hex(uint16_t value) ;
void printSerialNumber(uint16_t serial0, uint16_t serial1, uint16_t serial2) ;
bool read_CO2() ;
void set_CO2() ;
void setup() ;
void loop() ;
bool I2C_SW(byte cn) ;
void readHYT939(float *Temp, float *RH, float *DewPoint) ;
float readNTC(byte n) ;


#include "exampleUsage.ino"

#endif
