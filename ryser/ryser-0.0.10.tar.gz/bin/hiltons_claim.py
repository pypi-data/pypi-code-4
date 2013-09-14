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

import ryser

n = int(argv[1])
m = int(argv[2])

S = [6,7,11,15,18,19,20]

ryser.hall.on_interval(ryser.examples.eg1, ryser.examples.fail1[0], S, n, m)

