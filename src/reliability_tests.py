'''
reliability_tests.py
6/27/23

@author Ethan Mayer

Copyright 2023. All rights reserved.
'''


import time
from datetime import datetime, timedelta
from csv import writer
from os import popen
import os.path
import sys
import psutil

# Reliability testing suite class
class reliability_tests:

    ####################################################################################
    # Class variables
    first = False # Initialize start flag for read_usb
    expected_usb = "" # Correct list of USB

    ####################################################################################
    # Functions

    # Reads CPU die temperature from cmdline vcgencmd, accurate due to firmware-level request
    # temp=##.#'C where # = some number, desired result always 4 characters long
    def read_temperature():
        str = popen("vcgencmd measure_temp").read()
        temp = str[str.find("=")+1:-3] # Trim to cut off temp= and 'C
        #print(str)
        return temp

    # Reads CPU frequency from cmdline vcgencmd, accurate due to firmware-level request
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

    # Reads Pi voltage from cmdline vcgencmd, accurate due to firmware-level request
    # volt=#.####V where # = some number, desired result always 4 characters long
    def read_voltage(verbose):
        # Core voltage is voltage of CPU
        str = popen("vcgencmd measure_volts core").read()
        voltage_core = str[str.find("=")+1:-2] # trim to cut off volt= and V

        # If in verbose mode, only check and return voltage_core
        if verbose:
            return voltage_core
        
        # If not in verbose mode, check and return everything
        else:

            # sdram_c voltage is voltage of memory controller
            str = popen("vcgencmd measure_volts sdram_c").read()
            voltage_sdramc = str[str.find("=")+1:-2] # trim to cut off volt= and V

            # sdram_i voltage is voltage of memory I/O
            str = popen("vcgencmd measure_volts sdram_i").read()
            voltage_sdrami = str[str.find("=")+1:-2] # trim to cut off volt= and V

            # sdram_p voltage is voltage of physical memory
            str = popen("vcgencmd measure_volts sdram_p").read()
            voltage_sdramp = str[str.find("=")+1:-2] # trim to cut off volt= and V

            return [voltage_core, voltage_sdramc, voltage_sdrami, voltage_sdramp]

    # Reads throttle status from cmdline vcgencmd, accurate due to firmware-level request
    # throttled=#x# where # = some number (but little x always there because Hex), desired result always 3 characters long
    def read_throttle():
        str = popen("vcgencmd get_throttled").read()
        throttle = str[str.find("x")+1:-1] # trim to cut off throttled=#x
        # print(str)
        return throttle

    # Reads USB device status
    # Custom check, this checks and stores all usb devices at the start of the test and checks if it changes throughout the test
    def read_usb(self):
        str = popen("lsusb").read()

        # First time, check current USB devices and record them
        if not self.first:
            first = True
            expected_usb = str
            return 1
        
        # Every other time, check current USB devices against original recording
        else:
            # Ensure proper equality test by removing all forms of whitespace (spaces, tabs, indents, newlines, etc.)
            return int("".join(str.split()) == "".join(expected_usb.split()))

        ###### UNUSED, may use later?
        # Expected USB devices to be listed as seen in lab testing
    #     expected_usb = '''Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    # Bus 001 Device 025: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
    # Bus 001 Device 024: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T
    # Bus 001 Device 023: ID 0c45:6366 Microdia Webcam Vitade AF
    # Bus 001 Device 022: ID 2109:2817 VIA Labs, Inc. USB2.0 Hub
    # Bus 001 Device 021: ID 0c45:6366 Microdia Webcam Vitade AF
    # Bus 001 Device 015: ID 0403:6001 Future Technology Devices International, Ltd FT232 Serial (UART) IC
    # Bus 001 Device 003: ID 0c45:6366 Microdia Webcam Vitade AF
    # Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
    # Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub'''
        #########

    # Reads CPU utilization percentage
    def read_utilization():
        # Get cpu statistics
        cpu = str(psutil.cpu_percent()) + '%'
        return cpu

    # Reads RAM information
    def read_memory():
        memory = psutil.virtual_memory()
        # Convert Bytes to MB (Bytes -> KB -> MB)
        available = round(memory.available/1024.0/1024.0,1)
        total = round(memory.total/1024.0/1024.0,1)
        percent = str(memory.percent) + '%'
        return [available, percent]

    # UNUSED
    # Reads disk usage information
    def read_disk():
        # Calculate disk information
        disk = psutil.disk_usage('/')
        # Convert Bytes to GB (Bytes -> KB -> MB -> GB)
        free = round(disk.free/1024.0/1024.0/1024.0,1)
        total = round(disk.total/1024.0/1024.0/1024.0,1)
        percent = str(disk.percent) + '%'
        return [free, percent]

    # Append a list as a row to the CSV
    def append_list_as_row(write_obj, list_of_elem):
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

    # Starts test suite using functions above
    def start_tests(self, total_time, verbose):

        # Log normally if not verbose mode
        if not verbose:

            # Initialize CSV file for recording IMU data
            if not os.path.exists("../data"):
                os.makedirs("../data")
            timestr = time.strftime("%Y%m%d-%H%M%S")
            file_name = "../data/LOG_" + timestr + ".PiReadings.csv"
            open(file_name, 'w+', newline='')
                
            # Starts running the mission loop that continually checks data
            try:

                # Open file in append mode
                with open(file_name, 'a+', newline='') as write_obj:
                    # Write column titles to csv
                    csvTitles = ["Time (s)", "USB Status", "CPU Temperature ('C)", "CPU Utilization (%)", "Throttle Status", "CPU Frequency (hz)", "Core Frequency (hz)", "CPU Voltage (V)", "Memory Controller Voltage (V)", "Memory I/O Voltage (V)", "Memory Chip Voltage (V)", "Memory Free (Mb)", "Memory Free Percent (%)"]
                    self.append_list_as_row(write_obj, csvTitles)

                    # Get current time to use as baseline
                    start = datetime.now()
                    delt = timedelta(seconds=0)

                    # Only run for specified time
                    while ((delt.seconds / 60) < total_time):
                        # Only record time since start (starts at 0, incrments)
                        now = datetime.now()
                        delt = now - start

                        # Create list of all data for csv
                        # [time, temp, throttle, arm freq, core freq, sdram_c voltage, sdram_i voltage, sdram_p voltage]
                        csvList = [str(delt.seconds) + "." + str(round(delt.microseconds / 1000)), self.read_usb(), self.read_temperature(), self.read_utilization(), self.read_throttle()]
                        csvList.extend(self.read_frequency())
                        csvList.extend(self.read_voltage())
                        csvList.extend(self.read_memory())

                        # Write list to csv
                        self.append_list_as_row(write_obj, csvList)

                        # Sleep 100ms, but 80ms seems to be maximum frequency when checking data + writing to csv
                        time.sleep(0.1)

            # Stop logging on keyboard interrupt
            except KeyboardInterrupt:
                print("Stopping logging due to keyboard interrupt") #ctrl-c

        # If in verbose mode, do not log and just print output (for observation)
        else:

            print("===============Reliability Tests===============")
            print("USB Status\tCPU Temperature ('C)\tCPU Utilization (%)\tThrottle Status\tCPU Frequency (hz)\tCore Frequency (hz)\tCPU Voltage (V)\t")
            
            # Get current time to use as baseline
            start = datetime.now()
            delt = timedelta(seconds=0)

            # Only run for specified time
            while ((delt.seconds / 60) < total_time):
                sys.stdout.write("\r{}\t{}\t{}\t{}\t{}\t{}\t{}\t".format(self.read_usb(), self.read_utilization(), self.read_throttle(), self.read_frequency(), self.read_voltage(verbose)))
                sys.stdout.flush()

                # Sleep 100ms, but 80ms seems to be maximum frequency when checking data + writing to csv
                time.sleep(0.1)

    ############### Deprecated run loop for printing but may be used later by driver file

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