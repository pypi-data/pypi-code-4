#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import everysport
import logging
import os

'''Getting the Everysport APIKEY from the system environment. 

You need to set this with: 

    export EVERYSPORT_APIKEY={YOUR KEY}
'''
APIKEY = os.environ['EVERYSPORT_APIKEY'] 


class TestApi(unittest.TestCase):

    def setUp(self):        
        self.api = everysport.Api(APIKEY)


    def test_api(self):
        self.assertTrue(self.api)

    def test_unauthorized(self):
        foo = everysport.Api("foo")
        with self.assertRaises(everysport.EverysportException):
            foo.get_event(2129667)



if __name__ == '__main__': 
    logging.basicConfig(filename='api.log', 
                        level=logging.DEBUG, 
                        filemode="w") 
    unittest.main()