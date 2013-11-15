#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest 
from formv.exception import Invalid
from formv.validators.network import *

class Test(unittest.TestCase):
    def test(self):        
        self.assertIsNone(VIPAddress().validate(None))
        self.assertEqual('127.0.0.1', VIPAddress().validate('127.0.0.1'))
        self.assertEqual('2001:db8::ff00:42:8329', 
                         VIPAddress().validate('2001:0db8:0000:0000:0000:ff00:0042:8329'))        
        
        self.assertEqual('127.0.0.1/32', VCIDR().validate('127.0.0.1'))
        self.assertEqual('2001:db8::ff00:42:8329/64', 
                         VCIDR().validate('2001:0db8:0000:0000:0000:ff00:0042:8329'))
        
        self.assertRaises(Invalid, VCIDR().validate, *('127.0.0.1/64',))
        
        self.assertEqual('84:3A:4B:22:AB:30', VMACAddress().validate('84-3a-4b-22-ab-30'))
        self.assertRaises(Invalid, VMACAddress().validate, *('84-3a-4b-22-aX-30',))        