# Copyright 2021 Jason Bakos, Philip Conrad, Charles Daniels
#
# Part of the University of South Carolina CSCE491 course materials. Used by
# instructors for test case generators. Do not redistribute.

import sys
import os

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


sys.stderr.write("read a waves file with {} signals and {} samples\n".format(len(w.signals()), w.samples()))
sys.stderr.write("input has these signals:\n")
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
    if cpolVal == 0 and cphaVal == 1 and ssVal == 0 and sclkVal == 0 and prevSclk == 1:
        mosiList = mosiList + str(mosiVal)
        misoList = misoList + str(misoVal)
    if cpolVal == 1 and cphaVal == 0 and ssVal == 0 and sclkVal == 0 and prevSclk == 1:
        mosiList = mosiList + str(mosiVal)
        misoList = misoList + str(misoVal)
    if cpolVal == 1 and cphaVal == 1 and ssVal == 0 and sclkVal == 1 and prevSclk == 0:
        mosiList = mosiList + str(mosiVal)
        misoList = misoList + str(misoVal)
    prevSclk = sclkVal


## Binary to Hex Converter
def Hex(binary):
    return f"{int(binary, 2):02x}"
    
## Binary to Decimal Converter
def Decimal(binary):
    return f"{int(binary, 2):02}"
    
## Removes the leftover bits
limit = (len(mosiList) // 16) * 16
sys.stderr.write("\n\n{}".format(limit))

## Function to print out Read/Write
def RDWR(index):
    if mosiList[index + 6] == "0":
        return "RD"
    elif mosiList[index+6] == "1":
        return "WR"
    else:
        return "ERROR"

###################### Main Loop ######################
i = 0
while i < len(mosiList):
    # Need at least 16 bits for header
    if i + 16 > len(mosiList):
        break
    address = mosiList[i : i + 6]
    ##sys.stderr.write("\n\n{}".format(address))
    
    SIST = mosiList[i + 7]
    ##sys.stderr.write("\n\n{}".format(SIST))
    
    ## Used if stream bit = 0
    if SIST == "0":
        if RDWR(i) == "RD":
            data = misoList[i + 8 : i + 16]
        elif RDWR(i) == "WR":
            data = mosiList[i + 8 : i + 16]
        
        sys.stdout.write("{} {} {}\n".format(RDWR(i), Hex(address), Hex(data)))
        i = i + 16
    elif SIST == "1":
        stream = mosiList[i + 8 : i + 16]
        streamval = Decimal(stream)
        sys.stdout.write("{} STREAM {}".format(RDWR(i), Hex(address)))
        RDWRval = RDWR(i)
        i = i + 16
        for j in range (int(streamval)):
            if RDWRval == "RD":
                data = misoList[i : i + 8]
            elif RDWRval == "WR":
                data = mosiList[i : i + 8]
            sys.stdout.write(" {}".format(Hex(data)))
            i = i + 8
        sys.stdout.write("\n")
        


'''

def LongString(column):
    result = ""
    for i in range(w.samples()):
        edge_time = 0 if i == 0 else 1000.0 + (i-1) * 50
        
        # This adds the quotes needed for the tool's internal lookup
        columnName = f'"{column}"' 
        val = w.signalAt(columnName, edge_time)
        
        result += str(val)
        sys.stderr.write(str(val))
    return result


for i in range(w.samples()):
    if i == 0:
        edge_time = 0
    else:
        edge_time = 1000.0 + (i-1) * 50

    ssVal = w.signalAt("ss", edge_time)
    sclkVal = w.signalAt("sclk", edge_time)
    if ssVal == 0 and sclkVal == 1:
        mosiVal = w.signalAt("mosi", edge_time)
        mosiList = mosiList + str(mosiVal)
        
        misoVal = w.signalAt("miso", edge_time)
        misoList = misoList + str(misoVal)
    
    ##sys.stderr.write("{}".format(mosiVal))
    ##sys.stderr.write("{}".format(misoVal))
sys.stderr.write("\n\n{}".format(mosiList))
#sys.stderr.write("\n\n{}".format(misoList))




binary_str = "10101011"
# Lowercase without 0x
print(f"{int(binary_str, 2):x}")  # Output: 'ab'
# Uppercase without 0x
print(f"{int(binary_str, 2):X}")  # Output: 'AB'







def FindEchoTime(sample):
    for i in range(w.samples()):
        if i ==0:
            edge_time = 0
        else:
            edge_time = 1000.0 + (i-1) * 50
    return edge_time
    
sys.stderr.write("value at edge:{}\n".format(FindEchoTime(w.samples())))
  






for i in range(w.samples()):
    if i ==0:
        edge_time = 0
    else:
        edge_time = 1000.0 + (i-1) * 50
    
for s in range(6):
    val = w.signalAt("mosi", edge_time)
    sys.stderr.write(",{}".format(val))

# val = w.signalAt("mosi", 1000.0)
# sys.stderr.write("value at edge:{}\n".format(val))
'''























