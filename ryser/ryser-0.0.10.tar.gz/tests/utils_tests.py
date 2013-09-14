import unittest

from ryser.utils import list_assignment

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

class TestListAssignment(unittest.TestCase):
    def test_list_assignment(self):
        self.assertEqual(l1, {(0,0):[1]})
        self.assertEqual(l2, {(0,0):[1],(0,1):[2],(1,0):[2],(1,1):[1]})
        self.assertEqual(l3, {(0,1):[2],(1,2):[1],(0,0):[1],(2,1):[1],(1,1):[3],(2,0):[3],(2,2):[2],(1,0):[2],(0,2):[3]})


