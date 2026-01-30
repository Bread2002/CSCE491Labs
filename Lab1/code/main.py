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
##for s in w.signals():
    ##sys.stderr.write("\t* {} ({} bits)\n".format(s, w.sizes[s])) 
   
   
"""
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
"""    


mosiList = ""
misoList = ""
for i in range(w.samples()):
    if i ==0:
        edge_time = 0
    else:
        edge_time = 1000.0 + (i-1) * 50


    mosiVal = w.signalAt("mosi", edge_time)
    mosiList = mosiList + str(mosiVal)
    
    misoVal = w.signalAt("miso", edge_time)
    misoList = misoList + str(misoVal)
    
    ##sys.stderr.write("{}".format(mosiVal))
    ##sys.stderr.write("{}".format(misoVal))
sys.stderr.write("\n\n{}".format(mosiList))
#sys.stderr.write("\n\n{}".format(misoList))

## Binary to Hex Converter
def Hex(binary):
    return f"{int(binary, 2):02x}"
    
## Removes the leftover bits
limit = (len(mosiList) // 16) * 16

## Function to print out Read/Write
def RDWR(index):
    if mosiList[index + 6] == "0":
        return "RD"
    elif mosiList[index+6] == "1":
        return "WR"
    else:
        return "ERROR"

## Main Loop
for i in range(0, limit, 16):
    address = mosiList[i : i + 6]
    sys.stderr.write("\n\n{}".format(address))
    
    SIST = mosiList[i + 7]
    sys.stderr.write("\n\n{}".format(SIST))
    
    if RDWR(i) == "RD":
        data = mosiList[i + 7 : i + 16]
    elif RDWR(i) == "WR":
        data = misoList[i + 7 : i + 16]
    
    sys.stdout.write("{} {} {}\n".format(RDWR(i), Hex(address), Hex(data)))





'''
binary_str = "10101011"
# Lowercase without 0x
print(f"{int(binary_str, 2):x}")  # Output: 'ab'
# Uppercase without 0x
print(f"{int(binary_str, 2):X}")  # Output: 'AB'
'''





"""
def FindEchoTime(sample):
    for i in range(w.samples()):
        if i ==0:
            edge_time = 0
        else:
            edge_time = 1000.0 + (i-1) * 50
    return edge_time
    
sys.stderr.write("value at edge:{}\n".format(FindEchoTime(w.samples())))
 """   





"""
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
"""






















