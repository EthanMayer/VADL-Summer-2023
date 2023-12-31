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
import time
import git

# Reliability tests code import
import reliability_tests

# Script must be run using sudo, check for it
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo' in front. Exiting.")

# Handle command-line arguments
parser = argparse.ArgumentParser(prog = "Reliability Tests", description = "Author: Ethan Mayer\nThis program is designed to run tests on the reliability of payload electromechanical systems.")

# CLI argument for time
parser.add_argument("-T", "--time", type = int, help = "Length of time to run the tests in minutes (int)")

# CMDline argument for stress
parser.add_argument("-N", "--name", type = str, help = "Name of the log file to be recorded (requires non-verbose mode, timestamp will remain in name) (string)")

# CLI argument for stress
parser.add_argument("-S", "--stress", help = "Whether to stress the CPU, I/O, and Memory to 100%%", action = "store_true")

# CLI argument for verbose
parser.add_argument("-V", "--verbose", help = "Whether to print data to the terminal ONLY (no logging)", action = "store_true")

# Parse the provided arguments
args = parser.parse_args()

if args.verbose and args.name is not None:
    exit("You cannot specify both -V (verbose mode) and -N (name) because no log file will be created in verbose mode. Exiting.")

# Ensure software is up to date automatically
print("===============Pre-Test===============")
print("Running git pull to ensure test software is up-to-date. . .")
git_ssh_identity_file = "/home/vadl/.ssh/id_ed25519"
git_ssh_cmd = "ssh -i %s" % git_ssh_identity_file
repo = git.Repo('../.')
with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
    repo.git.pull()

# Print all parameters back so the user knows they are correct
print("===============Test Information===============")
print("Specified total length of tests:\t\t\t\t\t" + str(args.time) + " minute")
if args.name is not None:
    print("Specified name of log file (printed after file timestamp):\t\t" + args.name)
print("Stress the CPU, I/O, and Memory to 100%:\t\t\t\t" + str(args.stress))
print("Run in verbose mode and print data to terminal instead of logfile:\t" + str(args.verbose))

# Create the test object
tests = reliability_tests.reliability_tests()

try:
    # If specified, run the stress shell command as a parallel subprocess
    if args.stress:
        stress_proc = subprocess.Popen(["sudo", "stress", "--cpu", "4", "--io", "4", "--vm", "4"], text = False)

    # Start tests with specified time and verbose mode
    tests.start_tests(args.time, args.name, args.verbose)

except Exception as e:
    # If running, stop stressing when tests finish
    if args.stress:
        stress_proc.kill()

    # Print exception that occurred
    print("\nDRIVER EXCEPTION:\n" + str(e))

    exit()

# If running, stop stressing when tests finish
if args.stress:
    stress_proc.kill()

# Committing and uploading data automatically
print("===============Post-Test===============")
if not args.verbose:
    print("Running git commit and git push to ensure data is uploaded. . .")
    with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        repo.git.add(all = True)
        if args.name:
            repo.git.commit("-m", "Pi test data - " + args.name)
        else:
            repo.git.commit("-m", "Pi test data")
        repo.git.push()

# Restart automatically after the test finishes in order to clear throttle status register
print("Rebooting now to ensure throttle register is cleared. Goodbye.")
os.popen("sudo reboot")