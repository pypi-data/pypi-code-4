# -*- coding: utf-8 -*-
import unittest, os
import sys
sys.path.append("..")
from pyhole.jsoned import PyHoleJsoned
    

class TestPyHoleConnection(unittest.TestCase):
    def setUp(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.pyhole = PyHoleJsoned('file://' + self.path, force_slash=False)

    def test_get(self):
        self.assertEqual(self.pyhole.json.get(), [1,2,3, {'one':1, 'two':2}])
    def test_post(self):
        self.assertEqual(self.pyhole.json.get(), [1,2,3, {'one':1, 'two':2}])
    

        

if __name__ == '__main__':
    unittest.main()