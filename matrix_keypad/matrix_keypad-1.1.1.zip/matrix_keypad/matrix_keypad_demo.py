#!/usr/bin/python

from time import sleep
 
#Select which IO version by commenting the unused version 
from matrix_keypad import MCP230xx
#from matrix_keypad import RPi_GPIO
 
# Initialize the keypad class.
#   Uncommont the matching initialzation to the imported package from above
#   Using the **optional** variable "columnCount" to change it to a 4x4 keypad
kp = MCP230xx.keypad(address = 0x21, num_gpios = 8, columnCount = 4)
# kp = RPi_GPIO.keypad(ColumnCount = 3)
 
def digit():
    # Loop while waiting for a keypress
    r = None
    while r == None:
        r = kp.getKey()
    return r 
 
print "Please enter a 4 digit code: "
 
# Getting digit 1, printing it, then sleep to allow the next digit press.
d1 = digit()
print d1
sleep(1)
 
d2 = digit()
print d2
sleep(1)
 
d3 = digit()
print d3
sleep(1)
 
d4 = digit()
print d4
 
# printing out the assembled 4 digit code.
print "You Entered %s%s%s%s "%(d1,d2,d3,d4) 
