#!/usr/bin/env python3
"""Communicate with MARTA via MODBUS,"""
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import encode_ieee, decode_ieee, long_list_to_word, word_list_to_long, get_bits_from_int


class FloatModbusClient(ModbusClient):
    """A ModbusClient class with float support."""

    def read_float(self, address, number=1):
        """Read float(s) with read holding registers."""
        reg_l = self.read_holding_registers(address, number * 2)
        if reg_l:
            return [decode_ieee(f) for f in word_list_to_long(reg_l, big_endian=False)]
        else:
            return None

    def write_float(self, address, floats_list):
        """Write float(s) with write multiple registers."""
        b32_l = [encode_ieee(f) for f in floats_list]
        b16_l = long_list_to_word(b32_l,big_endian=False) 
        return self.write_multiple_registers(address, b16_l)
    
    def int_to_bool(self,word):
        return get_bits_from_int(word)


class Marta(object):
    """Communicate with MARTA via MODBUS."""

    read_register_map = {
        "PT01_R452A": 100,
        "PT03_R452A": 102,
        "PT04_R452A": 104,
        "PT01_CO2": 106,
        "PT02_CO2": 108,
        "PT03_CO2": 110,
        "PT04_CO2": 112,
        "PT05_CO2": 114,
        "PT06_CO2": 116,
        "TT01_R452A": 118,
        "TT02_R452A": 120,
        "TT03_R452A": 122,
        "TT04_R452A": 124,
        "TT01_CO2": 126,
        "TT02_CO2": 128,
        "TT03_CO2": 130,
        "TT04_CO2": 132,
        "TT05_CO2": 134,
        "TT06_CO2": 136,
        "TT07_CO2": 138,
        "FT01_CO2": 140,
        "SH01_R452A": 142,
        "SH03_R452A": 144,
        "ST01_R452A": 146,
        "ST03_R452A": 148,
        "ST01_CO2": 150,
        "ST02_CO2": 152,
        "ST03_CO2": 154,
        "ST04_CO2": 156,
        "ST05_CO2": 158,
        "ST06_CO2": 160,
        "SC01_CO2": 162,
        "SC02_CO2": 164,
        "SC03_CO2": 166,
        "SC04_CO2": 168,
        "SC05_CO2": 170,
        "SC06_CO2": 172,
        "DP01_CO2": 174,
        "DP02_CO2": 176,
        "DP03_CO2": 178,
        "DP04_CO2": 180,
        "DT02_CO2": 182,
        "DT03_CO2": 184,
        "DP_EV3C_CO2": 186,
        "SC01_CO2_Start": 190,
        "EV1": 192,
        "EV2": 194,
        "EV3": 196,
        "EV3C": 198,
    }

    write_register_map = {
        "LP_speed": 200,
        "EH_power": 202,
        "Temp": 204,
        "Speed": 206,
        "Flow": 208,
        "TC04_TSP": 210,
    }
    


    def __init__(self):
        pass

    def connect(self, host, port=502, slaveID=1):
        """Initialize the MODBUS client."""
        try:
            self.client = FloatModbusClient(host=host, port=port, unit_id=slaveID, auto_open=True, auto_close=False, debug=False)

        except ValueError:
            print("Errot setting up Modbus Client")
            self.client = None
            
            
    def discconect(self):
        self.client.close()
        
        
    def getattribute(self, name):
        """Check that we are asking to access a register."""
        if name in Marta.read_register_map:
            return self.get_float_register(Marta.read_register_map[name])

        else:
            return super(Marta, self).__getattribute__(name)

    def get_float_register(self, address, nreg=1):
        """Get the float register."""

        #print("Getting register at address {}".format(address))
        val = self.client.read_float(address, nreg)
        if val is None:
            return None
        else:
            return val[0]

    def get_alarms(self):
        """Get the alarms."""
        a1 = self.client.read_holding_registers(302)
        a2 = self.client.read_holding_registers(303)
        return a1, a2
        

    def get_status(self):
        """Get Marta Status."""
        reg_l = self.client.read_holding_registers(320)
        if reg_l is None:
            return None
        else:
            return reg_l[0]

    def set_temp_setpoint(self, value):
        """Set the temperature."""
        self.client.write_float(310, [value])

    def get_temp_setpoint(self):
        """Get the temperature setpoint."""
        return self.get_float_register(204)

    def set_speed_setpoint(self, value):
        """Set the speed setpoint."""
        self.client.write_float(312, [value])

    def get_speed_setpoint(self):
        """Get Speed setpoint."""
        return self.get_float_register(206)

    def set_flow_setpoint(self, value):
        """Set the flow setpoint."""
        self.client.write_float(314, [value])

    def get_flow_setpoint(self):
        """Get flow setpoint."""
        return self.get_float_register(208)
    
  
    def start_chiller(self, flow_active):
        """Starts chiller."""
        word = 1
        if flow_active:
            word = 5
        
        self.client.write_multiple_registers(305, [word])


        
    def start_co2(self, flow_active):
        """Starts co2."""
        "0000 -->nada"
        """0001 -->chiller fix speed"""
        """0101 -->chiller fix flow"""
        """0011 -->co2 fix speed"""
        """0111 -->co2 fix flow"""
        word = 3
        if flow_active:
            word = 8
                
        self.client.write_multiple_registers(305, [word])
    
    def stop_marta(self, flow_active):
        """Stop all."""
        
        self.client.write_multiple_registers(305, [0])



if __name__ == "__main__":
    marta = marta = Marta("147.156.52.123")
    oo = marta.get_status()
    print(oo)

    a1, a2 = marta.get_alarms()
    print("%x %x" % (a1, a2))

    print("bye")
    


