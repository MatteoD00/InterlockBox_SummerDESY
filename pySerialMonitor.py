# Script to test Arduino-Python interface --> Simulating the Serial Monitor included in the IDE
import serial
import time

def readserial(comport, baudrate, timestamp=False):
    ser = serial.Serial(comport, baudrate, timeout=0.1)         # 1/timeout is the frequency at which the port is read

    while True:

        data = ser.readline().decode().strip()

        if data and timestamp:
            timestamp = time.strftime('%H:%M:%S')
            print(f'{timestamp} > {data}')
        elif data:
            print(data)


while True:

    readserial('/dev/cu.usbmodem14201', 115200, True)