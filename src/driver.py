'''
driver.py
7/3/23

@author Ethan Mayer

Copyright 2023. All rights reserved.
'''

# Library imports
import argparse
import subprocess
import os

# Reliability tests code import
import reliability_tests

# Script must be run using sudo, check for it
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo' in front. Exiting.")

# Handle command-line arguments
parser = argparse.ArgumentParser(prog = "Reliability Tests", description = "This program is designed to run tests on the reliability of payload electromechanical systems.")

# CMDline argument for time
parser.add_argument("-T", "--time", type = int, help = "Length of time to run the tests in minutes (int)")

# CMDline argument for stress
parser.add_argument("-S", "--stress", help = "Whether to stress the CPU, I/O, and Memory to 100%%", action = "store_true")

# CMDline argument for verbose
parser.add_argument("-V", "--verbose", help = "Whether to print data to the terminal ONLY (no logging)", action = "store_true")

# Parse the provided arguments
args = parser.parse_args()

# Create the test object
tests = reliability_tests.reliability_tests()

try:
    # If specified, run the stress shell command as a parallel subprocess
    if args.stress:
        stress_proc = subprocess.Popen(["sudo", "stress", "--cpu", "4", "--io", "4", "--vm", "4"], text = False)

    # Start tests with specified time and verbose mode
    tests.start_tests(args.time, args.verbose)

except Exception as e:
    # If running, stop stressing when tests finish
    if args.stress:
        stress_proc.kill()

    # Print exception that occurred
    print("\nEXCEPTION:\n" + str(e))

# If running, stop stressing when tests finish
if args.stress:
    stress_proc.kill()