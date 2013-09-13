#!/usr/bin/python

# Testing Hilton's claim on p.5 of:
#   "CPLS: Cropper's Question" by Bobga, Goldwasser, Hilton and Johnson.
#

# . . 7 3 5 . . 
# . . . . 6 1 5 
# . 6 . . . . 3
# 6 . . . . . .
# 4 . . . . . . 
# 2 . 1 . . . . 
# 3 4 2 . . . . 

from sys import argv

from ryser.examples import eg1, fail1
from ryser.hall import is_hall_on_interval

n = int(argv[1])
m = int(argv[2])

is_hall_on_interval(eg1, fail1[0], [6,7,11,15,18,19,20], n, m)

