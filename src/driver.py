'''
driver.py
7/3/23

@author Ethan Mayer

Copyright 2023. All rights reserved.
'''

import argparse
import time
from datetime import datetime

# Handle command-line arguments
parser = argparse.ArgumentParser()

# CMDline argument for time
parser.add_argument("-T", "--time", type = int, help = "Length of time to run the tests in minutes (int)")

# CMDline argument for verbose
parser.add_argument("-V", "--verbose", help = "Whether to print data to the terminal", action = "store_true")

# CMDline argument for stress
parser.add_argument("-S", "--stress", help = "Whether to stress the CPU, I/O, and Memory to 100%", action = "store_true")

args = parser.parse_args()

# Get current time
now = datetime.now()