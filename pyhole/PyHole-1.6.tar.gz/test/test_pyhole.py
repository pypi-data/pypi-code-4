# -*- coding: utf-8 -*-
import unittest, os
import sys
sys.path.append("..")
from pyhole import PyHole

class TestPyHoleUrl(unittest.TestCase):
    def test_emptyurl(self):
        self.assertRaises(ValueError, PyHole, '')

    def test_single_getattr(self):
        pyhole = PyHole('http://domain.ltd', force_slash=True)
        self.assertEqual(str(pyhole.test), 'http://domain.ltd/test/')

    def test_single_getattr_no_trailing_slash(self):
        pyhole = PyHole('http://domain.ltd', force_slash=False)
        self.assertEqual(str(pyhole.test), 'http://domain.ltd/test')

    def test_noinput(self):
        pyhole = PyHole('http://domain.ltd', force_slash=True)
        self.assertEqual(str(pyhole), 'http://domain.ltd/')
        pyhole = PyHole('http://domain.ltd/', force_slash=True)
        self.assertEqual(str(pyhole), 'http://domain.ltd/')

    def test_noinput_no_trailing_slash(self):
        pyhole = PyHole('http://domain.ltd', force_slash=False)
        self.assertEqual(str(pyhole), 'http://domain.ltd')
        pyhole = PyHole('http://domain.ltd/', force_slash=False)
        self.assertEqual(str(pyhole), 'http://domain.ltd/')

    def test_multi_getattr(self):
        pyhole = PyHole('http://domain.ltd', force_slash=True)
        self.assertEqual(str(pyhole.one.two.tree), 'http://domain.ltd/one/two/tree/')       
        pyhole = PyHole('http://domain.ltd/', force_slash=True)
        self.assertEqual(str(pyhole.one.two.tree), 'http://domain.ltd/one/two/tree/')       

    def test_multi_getattr(self):
        pyhole = PyHole('http://domain.ltd', force_slash=False)
        self.assertEqual(str(pyhole.one.two.tree), 'http://domain.ltd/one/two/tree')       
        pyhole = PyHole('http://domain.ltd/', force_slash=False)
        self.assertEqual(str(pyhole.one.two.tree), 'http://domain.ltd/one/two/tree')       
    
    def test_getitem(self):
        pyhole = PyHole('http://domain.ltd', force_slash=True)
        self.assertEqual(str(pyhole['one']), 'http://domain.ltd/one/')       
        self.assertEqual(str(pyhole[123]), 'http://domain.ltd/123/')       
        self.assertEqual(str(pyhole[123][456]), 'http://domain.ltd/123/456/')       
        self.assertEqual(str(pyhole[123]['abc'][456]), 'http://domain.ltd/123/abc/456/')       

    def test_getitem_enc(self):
        pyhole = PyHole('http://domain.ltd', force_slash=True)
        self.assertEqual(str(pyhole['ąż ÓŁ +/']), r'http://domain.ltd/%C4%85%C5%BC%20%C3%93%C5%81%20%2B%2F/')       
    def test_params(self):
        pyhole = PyHole('http://domain.ltd', force_slash=False)
        self.assertEqual(str(pyhole['test.php']({'p1': 'v1'})), r'http://domain.ltd/test.php?p1=v1')       

    def test_multi_params(self):
        pyhole = PyHole('http://domain.ltd', force_slash=False)
        self.assertEqual(str(pyhole.some({'p2': 4, 'p3': 'v3'})['test.php']({'p1': 'v1'})), r'http://domain.ltd/some/test.php?p2=4&p3=v3&p1=v1')       
        self.assertEqual(str(pyhole('some', {'p2': 4, 'p3': 'v3'})['test.php']({'p1': 'v1'})), r'http://domain.ltd/some/test.php?p2=4&p3=v3&p1=v1')

class TestPyHoleConnection(unittest.TestCase):
    def setUp(self):
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.pyhole = PyHole('file://' + self.path, force_slash=False)

    def test_get(self):
        self.assertEqual(self.pyhole.plaintext.get(), 'plain text')
    
        

if __name__ == '__main__':
    unittest.main()
