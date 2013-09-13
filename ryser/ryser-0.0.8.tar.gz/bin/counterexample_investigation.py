#!/usr/bin/python

# Testing a potential counterexample.

#  2  6  7  8  9 10 11 12  .  .  .  .
#  6  2  8  7 10  9 12 11  .  .  .  .
#  7  8  1  6 11 12  9 10  .  .  .  .
#  8  7  6  1  2  3  4  5  .  .  .  .
#  9 10 11  2  3  4  5  1  .  .  .  .
# 10  9 12  3  4  5  1  2  .  .  .  .
# 11 12  9  4  5  1  2  3  .  .  .  .
# 12 11 10  5  1  2  3  4  .  .  .  .
#  .  .  .  .  .  .  .  .  .  2  .  .
#  .  .  .  .  .  .  .  .  2  .  .  .
#  .  .  .  .  .  .  .  .  .  .  .  9
#  .  .  .  .  .  .  .  .  .  .  9  .

from sys import argv

from ryser.examples import eg5
from ryser.hall import is_hall_on_interval
from ryser.utils import rect_r

n = int(argv[1])
m = int(argv[2])

TR = rect_r(9, 96, 12)
B1 = rect_r(107, 120, 12)
D = [105, 118, 131, 144]

constant = []
exponent = TR + B1 + D

is_hall_on_interval(eg5, constant, exponent, n, m)

