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
import os.path
from os import popen
# from gpiozero import CPUTemperature

# Reads CPU die temperature from cmdline vcgencmd
# temp=##.#'C where # = some number, desired result always 4 characters long
def read_temperature():
    str = popen("vcgencmd measure_temp").read()
    temp = str[str.find("=")+1:-3] # Trim to cut off temp= and 'C
    #print(str)
    return temp

# Reads CPU frequency from cmdline vcgencmd
# frequency(48)=######### where # = some number, desired result can be between 9-10 characters long
def read_frequency():
    # ARM frequency is frequency of the processor
    str = popen("vcgencmd measure_clock arm").read()
    freq_arm = str[str.find("=")+1:-1] # trim to cut off frequency(48)=
    # print(str)

    # Core frequency is frequency of the VPU/firmware/buses for peripherals
    str = popen("vcgencmd measure_clock core").read()
    freq_core = str[str.find("=")+1:-1] # trim to cut off frequency(48)=
    # print(str)

    return [freq_arm, freq_core]

# Reads Pi voltage from cmdline vcgencmd
# volt=#.####V where # = some number, desired result always 4 characters long
def read_voltage():
    # Core voltage is voltage of CPU
    str = popen("vcgencmd measure_volts core").read()
    voltage_core = str[str.find("=")+1:-2] # trim to cut off volt= and V
    # print(str)

    # sdram_c voltage is voltage of memory controller
    str = popen("vcgencmd measure_volts sdram_c").read()
    voltage_sdramc = str[str.find("=")+1:-2] # trim to cut off volt= and V
    # print(str)

    # sdram_i voltage is voltage of memory I/O
    str = popen("vcgencmd measure_volts sdram_i").read()
    voltage_sdrami = str[str.find("=")+1:-2] # trim to cut off volt= and V
    # print(str)

    # sdram_p voltage is voltage of physical memory
    str = popen("vcgencmd measure_volts sdram_p").read()
    voltage_sdramp = str[str.find("=")+1:-2] # trim to cut off volt= and V
    # print(str)

    return [voltage_core, voltage_sdramc, voltage_sdrami, voltage_sdramp]

# Reads throttle status from cmdline vcgencmd
# throttled=#x# where # = some number (but little x always there because Hex), desired result always 3 characters long
def read_throttle():
    str = popen("vcgencmd get_throttled").read()
    throttle = str[str.find("x")+1:-1] # trim to cut off throttled=#x
    # print(str)
    return throttle

# Reads USB device status
def read_usb():
    str = popen("lsusb").read()
    
    # Expected USB devices to be listed as seen in lab testing
    expected_usb = '''Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 025: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
Bus 001 Device 024: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
Bus 001 Device 023: ID 0c45:6366 Microdia Webcam Vitade AF
Bus 001 Device 022: ID 2109:2817 VIA Labs, Inc. USB2.0 Hub
Bus 001 Device 021: ID 0c45:6366 Microdia Webcam Vitade AF
Bus 001 Device 015: ID 0403:6001 Future Technology Devices International, Ltd FT232 Serial (UART) IC
Bus 001 Device 003: ID 0c45:6366 Microdia Webcam Vitade AF
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub'''

    # Ensure proper equality test by removing all forms of whitespace (spaces, tabs, indents, newlines, etc.)
    return int("".join(str.split()) == "".join(expected_usb.split()))

# Append a list as a row to the CSV
def append_list_as_row(write_obj, list_of_elem):
    # Create a writer object from csv module
    csv_writer = writer(write_obj)
    # Add contents of list as last row in the csv file
    csv_writer.writerow(list_of_elem)

# Initialize CSV file for recording IMU data ########################################
if not os.path.exists("../data"):
    os.makedirs("../data")
timestr = time.strftime("%Y%m%d-%H%M%S")
file_name = "../data/LOG_" + timestr + ".PiReadings.csv"
with open(file_name, 'w+', newline='') as file:
    new_file = writer(file)
    
# Starts running the mission loop that continually checks data
try:

    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Write column titles to csv
        csvTitles = ["Time", "USB Status", "CPU Temperature", "Throttle Status", "CPU Frequency", "Core Frequency", "CPU Voltage", "Memory Controller Voltage", "Memory I/O Voltage", "Memory Chip Voltage"]
        append_list_as_row(write_obj, csvTitles)

        # Get current time to use as baseline
        start = datetime.now()

        while True:
            # Only record time since start (starts at 0, incrments)
            now = datetime.now()
            delt = now - start

            # Create list of all data for csv
            # [time, temp, throttle, arm freq, core freq, sdram_c voltage, sdram_i voltage, sdram_p voltage]
            csvList = [str(delt.seconds) + "." + str(round(delt.microseconds / 1000)), read_usb(), read_temperature(), read_throttle()]
            csvList.extend(read_frequency())
            csvList.extend(read_voltage())

            # Write list to csv
            append_list_as_row(write_obj, csvList)

            # Sleep 1ms, but 50ms seems to be maximum frequency when checking data + writing to csv
            time.sleep(0.001)
except KeyboardInterrupt:
    print("Stopping logging due to keyboard interrupt") #ctrl-c

#### Deprecated run loop for printing but may be used later by driver file

# # Get current time to use as baseline
# start = datetime.now()
    
# # Run loop
# while True:
#     # Only record time since start (starts at 0, incrments)
#     now = datetime.now()
#     delt = now - start

#     print(str(delt.microseconds / 1000.0) + " READINGS:")

#     # Perform all sensor readings
#     read_temperature()
#     read_frequency()
#     read_voltage()
#     read_throttle()

#     # Sleep 1ms, but 34ms seems to be maximum frequency when just checking data
#     time.sleep(0.001)