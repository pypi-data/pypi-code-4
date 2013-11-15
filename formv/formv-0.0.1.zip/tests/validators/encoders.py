#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest 
from formv.exception import Invalid
from formv.validators.encoders import *
from formv.utils.encoding import crypt

class Test(unittest.TestCase):
    def test(self):
        
        self.assertIsNone(VEncoded().validate(None))
        value = {'username':None, 'password':None}
        self.assertEqual(None, 
                         VEncodedPair('password', 'Password', 
                                      'username').validate(value))
        
        u = 'dummy@dummy.com'; p = 'dummy-secret-password'  
        value = {'username':u, 'password':p}
              
        h = VEncoded().validate(p)
        self.assertEqual(h, crypt(p, h))
        
        h = VEncodedPair('password', 'Password', 
                         'username').validate(value)
        self.assertEqual(h, crypt(p+u, h))