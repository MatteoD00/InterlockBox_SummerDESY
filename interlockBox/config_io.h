#include <Arduino.h>
#ifndef CONFIG_IO_H
#define CONFIG_IO_H

#define SENS_PW 13	 // P-MOSFET activating I2C sensors power
#define RELAY1 A5
#define RELAY2 A6
#define RELAY3 0
#define RELAY4 1
#define ANALOG_PINS { 2, 3, 4 }
#define GPIO_PINS { 5, 4, 3, 2}
#define AnalogResolution 12  //10 bits
#define ADCvolts 3.3
#define ADCsteps 4095 // 12 bits
//#define ADCsteps 1023 // 10 bits
#define VOLTS	(ADCvolts/ADCsteps)

// I2C switch address
#define SW_ADDRS 		0x70	//0x70 to 0x77 depending on address pins
#define CHANNEL_NUM	4

#define DEFAULT_SHTXX_ADDRS 0x44

//Flow meter parameters
#define LOWSIG_FLOW 0.  // or 1 or 4
#define HISIG_FLOW 3.3 // or 5 or 20
#define MIN_FLOW 0.
#define MAX_FLOW 5.

#endif
