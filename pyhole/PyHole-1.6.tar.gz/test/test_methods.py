# -*- coding: utf-8 -*-
import unittest, os, time
import sys
sys.path.append("..")
from pyhole import PyHole
from httptestserver import HTTPTestServer


class TestPyHoleUrl(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPTestServer()
        cls.server.start()
    
    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        
    def test_get(self):
        pyhole = PyHole('http://localhost:8880', force_slash=True)        
        self.assertEqual(pyhole.test.get(), 'GET /test/')
        
    def test_post(self):
        pyhole = PyHole('http://localhost:8880', force_slash=True)        
        self.assertEqual(pyhole.test.post(data={"abc" :"abc"}), 'POST /test/')

    def test_put(self):
        pyhole = PyHole('http://localhost:8880', force_slash=True)        
        self.assertEqual(pyhole.test.put(), 'PUT /test/')

    def test_delete(self):
        pyhole = PyHole('http://localhost:8880', force_slash=True)        
        self.assertEqual(pyhole.test.delete(), 'DELETE /test/')

if __name__ == '__main__':
    unittest.main()
