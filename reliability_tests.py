'''
reliability_tests.py
6/27/23

@author Ethan Mayer

Copyright 2023. All rights reserved.
'''

import time
from csv import writer
from datetime import datetime
from datetime import timedelta
from os import popen
# from gpiozero import CPUTemperature

# Reads CPU die temperature from cmdline vcgencmd
# temp=##.#'C where # = some number, desired result always 4 characters long
def read_temperature():
    str = popen("vcgencmd measure_temp").read()
    temp = str[str.find("=")+1:-3] # Trim to cut off temp= and 'C
    print(str)

# Reads CPU frequency from cmdline vcgencmd
# frequency(48)=######### where # = some number, desired result can be between 9-10 characters long
def read_frequency():
    str = popen("vcgencmd measure_clock arm").read()
    freq = str[str.find("=")+1:-1] # trim to cut off frequency(48)=
    print(str)

# Reads Pi voltage from cmdline vcgencmd
# volt=#.####V where # = some number, desired result always 4 characters long
def read_voltage():
    str = popen("vcgencmd measure_volts").read()
    voltage = str[str.find("=")+1:-2] # trim to cut off volt= and V
    print(str)

# Reads throttle status from cmdline vcgencmd
# throttled=#x# where # = some number (but little x always there because Hex), desired result always 3 characters long
def read_throttle():
    str = popen("vcgencmd get_throttled").read()
    throttle = str[str.find("x")+1:-1] # trim to cut off throttled=#x
    print(str)

start = datetime.now()

while True:
    now = datetime.now()
    delt = now - start
    print(str(delt.microseconds) + "READINGS:")
    read_temperature()
    read_frequency()
    read_voltage()
    read_throttle()
    time.sleep(0.008)