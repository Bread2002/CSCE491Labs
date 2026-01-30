# Copyright 2021 Jason Bakos, Philip Conrad, Charles Daniels
#
# Part of the University of South Carolina CSCE491 course materials. Used by
# instructors for test case generators. Do not redistribute.

import sys
import os


# Helper function that prints out RD/WR
def RDWR(index):
    if mosiList[index + 6] == "0":
        return "RD"
    elif mosiList[index + 6] == "1":
        return "WR"
    else:
        return "ERROR"
    
    
# Helper function that converts binary to hex
def Hex(binary):
    return f"{int(binary, 2):02x}"


###############################################################################

# This block is setup code that loads the utility library for this assignment.
# You shouldn't mess with it unless you know what you are doing.

# this is the directory where our code is (main.py)
code_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]

# this will be ./.. - the project directory
parent_dir = os.path.split(code_dir)[0]

# the python utils live in ../utils/python_utils
python_utils_dir = os.path.join(parent_dir, "utils", "python_utils")

# append this to Python's import path and import it
sys.path.append(python_utils_dir)
from waves import Waves

###############################################################################

# Read in all the data from standard input and parse it.
w = Waves()
w.loadText(sys.stdin.read())

# Display some information about it. We can use sys.stderr.write() to send a
# log message to standard error without it interfering with the data we
# send to standard out for grade.sh to interpret.
sys.stderr.write("Read a waves file with {} signals and {} samples...\n".format(len(w.signals()), w.samples()))
sys.stderr.write("Input has these signals:\n")
for s in w.signals():
    sys.stderr.write("\t* {} ({} bits)\n".format(s, w.sizes[s])) 

mosiList = ""
misoList = ""
prevSclk = 0  # Track previous clock state to detect edges

# Extract MOSI and MISO data based on SCLK edges
for i in range(w.samples()):
    # Access signal values directly from the data structure
    # w.data[i] is a tuple: (timestamp, signals_dict)
    sclkVal = w.data[i][1]["sclk"]
    mosiVal = w.data[i][1]["mosi"]
    misoVal = w.data[i][1]["miso"]
    ssVal = w.data[i][1]["ss"]
    cpolVal = w.data[i][1]["cpol"]
    cphaVal = w.data[i][1]["cpha"]
    
    # Only capture on rising edge of sclk (0->1) when ss is active (ss==0)
    # This is for CPOL=0, CPHA=0 mode
    if cpolVal == 0 and cphaVal == 0 and ssVal == 0 and sclkVal == 1 and prevSclk == 0:
        mosiList = mosiList + str(mosiVal)
        misoList = misoList + str(misoVal)
    
    prevSclk = sclkVal

# sys.stderr.write("\nMOSI: {}\n".format(mosiList))
# sys.stderr.write("\nMISO: {}\n".format(misoList))
    
# Remove any leftover bits
limit = (len(mosiList) // 16) * 16

# Main Loop
for i in range(0, limit, 16):
    address = mosiList[i : i + 6]
    sys.stderr.write("\nAddress #{}: {}".format(i // 16 + 1, address))
    
    SIST = mosiList[i + 6]
    sys.stderr.write("\nSIST: {}".format(SIST))
    
    if RDWR(i) == "RD":
        data = misoList[i + 8 : i + 16]
    elif RDWR(i) == "WR":
        data = mosiList[i + 8 : i + 16]
    
    sys.stderr.write("\nExchange #{}: {}\n".format(i // 16 + 1, data))
    sys.stdout.write("{} {} {}\n".format(RDWR(i), Hex(address), Hex(data)))
