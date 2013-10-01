import unittest

from ryser.utils import list_assignment
from ryser.utils import alt, alt2

from ryser.examples import eg1

##########################################
# Testing of list_assignment
##########################################

size = 1
P1 = {1:1}
l1 = list_assignment(P1, size)

size = 2
P2 = {1:1, 2:2, 3:2, 4:1}
l2 = list_assignment(P2, size)

size = 3
P3 = {1:1, 2:2, 5:3, 6:1, 7:3}
l3 = list_assignment(P3, size)

P4 = {1:1, 2:2, 3:3, \
      4:2, 5:3, 6:1, \
      7:3, 8:1, 9:2}

P5 = eg1.fixed_cells()

class TestListAssignment(unittest.TestCase):
    def test_list_assignment(self):
        self.assertEqual(l1, {(0,0):[1]})
        self.assertEqual(l2, {(0,0):[1],(0,1):[2],\
                              (1,0):[2],(1,1):[1]})
        self.assertEqual(l3, {(0,0):[1],(0,1):[2],(0,2):[3],\
                              (1,0):[2],(1,1):[3],(1,2):[1],\
                              (2,0):[3],(2,1):[1],(2,2):[2],})

##########################################
# Testing of data conversions.
##########################################

X1 = {1: [(0, 0), (1, 1)],         \
      2: [(0, 1), (1, 0)]}

XX1 = {1: [(0, 0), (1, 2)],        \
       2: [(0, 1)],                \
       3: [(1, 1), (2, 0)]}

Y1 = {1: [(1, 2), (0, 0), (2, 1)], \
      2: [(0, 1), (2, 2), (1, 0)], \
      3: [(0, 2), (2, 0), (1, 1)]}

Z1 = {1: [(1, 5), (5, 2)],         \
      2: [(5, 0), (6, 2)],         \
      3: [(0, 3), (2, 6), (6,0)],  \
      4: [(4, 0), (6, 1)],         \
      5: [(0, 4), (1, 6)],         \
      6: [(1, 4), (2, 1), (3,0)],  \
      7: [(0, 2)]}

X2 = [{0:1,1:2},\
      {0:2,1:1}]

XX2 = [{0:1, 1:2}, \
       {1:3, 2:1}, \
       {0:3}]

Y2 = [{0:1,1:2,2:3},\
      {0:2,1:3,2:1},\
      {0:3,1:1,2:2}]

Z2 = [{2:7,3:3,4:5},
      {4:6,5:1,6:5},
      {1:6,6:3},
      {0:6},
      {0:4},
      {0:2,2:1},
      {0:3,1:4,2:2}]

class TestA(unittest.TestCase):
    def test_A(self):
        self.assertEqual(P2, alt(X1, 2))
        self.assertEqual(P3, alt(XX1, 3))
        self.assertEqual(P4, alt(Y1, 3))
        self.assertEqual(P5, alt(Z1, 7))

class TestA2(unittest.TestCase):
    def test_A2(self):
        self.assertEqual(P2, alt2(X2, 2))
        self.assertEqual(P3, alt2(XX2, 3))
        self.assertEqual(P4, alt2(Y2, 3))
        self.assertEqual(P5, alt2(Z2, 7))

if __name__ == '__main__':
    unittest.main()

