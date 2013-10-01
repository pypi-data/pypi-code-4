# Copyright Matthew Henderson 2013
# Created 1st April 2012.
# Last updated: Mon Sep 30 19:44:38 BST 2013.

import itertools

from ryser.designs import Latin
from ryser.utils import rect_r, col_r, row_r, from_file

source1 = open('/home/matthew/workspace/ryser/data/eg1.txt', 'rb')
source2 = open('/home/matthew/workspace/ryser/data/eg2.txt', 'rb')

eg1 = Latin(from_file(source1, 7), size = 7, format = 'alt2')
eg2 = Latin(from_file(source2, 8), size = 8, format = 'alt2')

# Below are lists of lists of cells. Each list represents a list of subgraphs
# for which Hall's condition or the symmetric Hall condition fails. They are
# independent of the examples to aid reuse.

# fail1 is the subgraph from the paper referenced in the comment about Latin
# 1. It's unlikely that this set is going to occur elsewhere so we won't attempt
# to generalise here.

fail1 = [[1,2, \
          8,9,10, \
          17, \
          23,24,25,26,27,28, \
          30,31,32,33,34,35, \
          37,39,40,41,42, \
          46,47,48,49]]

# A first attempt at generalisation.
# Here fail2 consists of the following 4 elements from an 8 x 8 matrix labelled
# 1,..,64 across rows from top-left to bottom-right.
#   * The first 6 rows of the second last column.
#   * The first 6 rows of the last column.
#   * The first 6 rows of the last two columns.
#   * All subsets of the first 6 rows of the last two columns which contain
#     exactly 11 elements.

fail2 = [col_r(7,8)[:-2], \
         col_r(8,8)[:-2], \
         col_r(7,8)[:-2] + col_r(8,8)[:-2]] + \
        [list(x) for x in itertools.combinations(col_r(7,8)[:-2] + col_r(8,8)[:-2], 11)]

# fail3 consists of the following 7 elements:
#    * The top right block (TRr) plus the top right block B1 of the
#      bottom right block (BR) as well as:
#      * all subsets we get from this set by removing a row from TRr.
#    * TR minus the first column (TRmc1) plus the first row of B1.
#    * TR minus the second column (TRmc2) plus the second row of B1.

B1 = [39,40,47,48]
r1 = row_r(1,8)[4:]
r2 = row_r(8 + 1,8)[4:]
r3 = row_r(2*8 + 1,8)[4:]
r4 = row_r(3*8 + 1,8)[4:]
c1 = col_r(5,8)[:4]
c2 = col_r(6,8)[:4]
TRr = rect_r(5, 32, 8)
TRmc1 = [x for x in TRr if x not in c1]
TRmc2 = [x for x in TRr if x not in c2]

temp = [B1 + reduce(lambda x,y: x+y, z) for z in itertools.combinations([r1,r2,r3,r4], 3)]
fail3 = temp + [
          B1 + TRr, \
          TRmc2 + B1[:2], \
          TRmc1 + B1[2:]]

"""
Example 3

This is Type 1, Case 2

 2 1 3 4 . . . .
 1 3 2 6 . . . .
 3 2 4 1 . . . .
 4 6 1 5 . . . .
 . . . . . 1 . .
 . . . . 1 . . .
 . . . . . . . 2
 . . . . . . 2 .

"""

eg3 = Latin(
      { 1:2,  2:1,  3:3,  4:4, \
        9:1, 10:3, 11:2, 12:6, \
       17:3, 18:2, 19:4, 20:1, \
       25:4, 26:6, 27:1, 28:5, \
       38:1, \
       45:1, \
       56:2, \
       63:2 }, size = 8)

fail4 = [ TRr + B1 ]

"""
Example 4

This is Type 2, Case 1

 1 2 3 5 . . . .
 2 1 3 6 . . . .
 3 1 4 2 . . . .
 5 6 2 1 . . . .
 . . . . . 1 . .
 . . . . 1 . . .
 . . . . . . . 2
 . . . . . . 2 .

"""

eg4 = Latin(
    { 1:1,  2:2,  3:3,  4:5, \
      9:2, 10:1, 11:3, 12:6, \
     17:3, 18:1, 19:4, 20:2, \
     25:5, 26:6, 27:2, 28:1, \
     38:1, \
     45:1, \
     56:2, \
     63:2 }, size = 8)

"""

Example 5

This is Type 1, Case 1

  2  6  7  8  9 10 11 12  .  .  .  .
  6  2  8  7 10  9 12 11  .  .  .  .
  7  8  1  6 11 12  9 10  .  .  .  .
  8  7  6  1  2  3  4  5  .  .  .  .
  9 10 11  2  3  4  5  1  .  .  .  .
 10  9 12  3  4  5  1  2  .  .  .  .
 11 12  9  4  5  1  2  3  .  .  .  .
 12 11 10  5  1  2  3  4  .  .  .  .
  .  .  .  .  .  .  .  .  .  2  .  .
  .  .  .  .  .  .  .  .  2  .  .  .
  .  .  .  .  .  .  .  .  .  .  .  9
  .  .  .  .  .  .  .  .  .  .  9  .

"""

eg5 = Latin(
    {   1: 2,   2: 6,  3: 7,  4: 8,  5: 9,  6:10,  7:11,  8:12, \
       13: 6,  14: 2, 15: 8, 16: 7, 17:10, 18: 9, 19:12, 20:11, \
       25: 7,  26: 8, 27: 1, 28: 6, 29:11, 30:12, 31: 9, 32:10, \
       37: 8,  38: 7, 39: 6, 40: 1, 41: 2, 42: 3, 43: 4, 44: 5, \
       49: 9,  50:10, 51:11, 52: 2, 53: 3, 54: 4, 55: 5, 56: 1, \
       61:10,  62: 9, 63:12, 64: 3, 65: 4, 66: 5, 67: 1, 68: 2, \
       73:11,  74:12, 75: 9, 76: 4, 77: 5, 78: 1, 79: 2, 80: 3, \
       85:12,  86:11, 87:10, 88: 5, 89: 1, 90: 2, 91: 3, 92: 4, \
      106: 2, 117: 2, \
      132: 9, 143: 9}, size = 12)

"""

Example 6

This is Type 2, Case 2

  4  1  2 10 11 12  .  .  .  .  .  .
  1  5 10 11 12  2  .  .  .  .  .  .
  2 10  6 12  1 11  .  .  .  .  .  .
 10 11 12  1  2  3  .  .  .  .  .  .
 11 12  1  2  3 10  .  .  .  .  .  .
 12  2 11  3 10  1  .  .  .  .  .  .
  .  .  .  .  .  .  .  1  .  .  .  .
  .  .  .  .  .  .  1  .  .  .  .  .
  .  .  .  .  .  .  .  .  .  1  .  .
  .  .  .  .  .  .  .  .  1  .  .  .
  .  .  .  .  .  .  .  .  .  .  .  2
  .  .  .  .  .  .  .  .  .  .  2  .

"""

eg6 = Latin(
    {   1: 4,   2: 1,  3: 2,  4:10,  5:11,  6:12, \
       13: 1,  14: 5, 15:10, 16:11, 17:12, 18: 2, \
       25: 2,  26:10, 27: 6, 28:12, 29: 1, 30:11, \
       37:10,  38:11, 39:12, 40: 1, 41: 2, 42: 3, \
       49:11,  50:12, 51: 1, 52: 2, 53: 3, 54:10, \
       61:12,  62: 2, 63:11, 64: 3, 65:10, 66: 1, \
       80: 1,  91: 1, \
      106: 1, 117: 1, \
      132: 2, 143: 2}, size = 12)

fail6 = [rect_r(7, 72, 12) + rect_r(83, 96, 12) + rect_r(107, 120, 12)]

"""
Example 8

Completable

 3 1 7 4 . . . .
 4 2 4 3 . . . .
 7 4 6 5 . . . .
 4 3 5 8 . . . .
 . . . . . 3 . .
 . . . . 3 . . .
 . . . . . . . 5
 . . . . . . 5 .

"""

eg8 = Latin({ 1:3,  2:1,  3:7,  4:4,\
              9:1, 10:2, 11:4, 12:3,\
             17:7, 18:4, 19:6, 20:5,\
             25:4, 26:3, 27:5, 28:8,\
             38:3, 45:3, \
             56:5, 63:5 }, size = 8)

