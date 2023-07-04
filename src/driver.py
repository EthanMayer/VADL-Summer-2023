'''
driver.py
7/3/23

@author Ethan Mayer

Copyright 2023. All rights reserved.
'''

import argparse
import time
from datetime import datetime
import reliability_tests
import subprocess

# Handle command-line arguments
parser = argparse.ArgumentParser()

# CMDline argument for time
parser.add_argument("-T", "--time", type = int, help = "Length of time to run the tests in minutes (int)")

# CMDline argument for verbose
parser.add_argument("-V", "--verbose", help = "Whether to print data to the terminal", action = "store_true")

# CMDline argument for stress
parser.add_argument("-S", "--stress", help = "Whether to stress the CPU, I/O, and Memory to 100%", action = "store_true")

# Parse the provided arguments
args = parser.parse_args()

# Create the test object
tests = reliability_tests.reliability_tests()

# If specified, run the stress shell command as a parallel subprocess
if args.verbose:
    stress_proc = subprocess.Popen(["sudo", "stress", "--cpu", "4", "--io", "4", "--vm", "4"])

# Start the tests for the specified time
tests.start_tests(args.time)

# If running, stop stressing when tests finish
if args.verbose:
    stress_proc.kill()