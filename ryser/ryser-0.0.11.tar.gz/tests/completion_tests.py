# Created: Tue Oct  1 13:21:28 BST 2013.
# Last updated: Tue Oct  1 13:21:38 BST 2013.

import unittest

import ryser

f = {1: 1, 3: 3, 4: 2, 5: 3, 8: 1, 9: 2}


class TestComplete(unittest.TestCase):
    """Testing of completion components.
    
    We should be careful not to writing tests that could be time
    consuming.
    """

    def setUp(self):
        pass

    def test_completion(self):
        P = ryser.designs.Latin(f, 3)
        L = ryser.completion.complete(P)
        self.assertEqual(L[0,0], 1)
        self.assertEqual(L[0,1], 2)
        self.assertEqual(L[0,2], 3)
        self.assertEqual(L[1,0], 2)
        self.assertEqual(L[1,1], 3)
        self.assertEqual(L[1,2], 1)
        self.assertEqual(L[2,0], 3)
        self.assertEqual(L[2,1], 1)
        self.assertEqual(L[2,2], 2)

