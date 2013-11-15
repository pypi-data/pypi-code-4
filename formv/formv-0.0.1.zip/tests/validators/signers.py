#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from formv.exception import Invalid
from formv.validators.signers import *

class Dummy(object):
    content = 'dummy'

class Test(unittest.TestCase):
    def test(self):
        key = 'dummy secret'
        dummy = Dummy()
        
        self.assertEqual(None, VSignedString(key=key).validate(VSignedString(key=key).sign('')))
        self.assertEqual(None, VSignedObject(key=key).validate(VSignedObject(key=key).sign('')))

        self.assertRaises(Invalid, VSignedString(key=key, required=True).validate, 
                          *(VSignedString(key=key).sign(''),))
        self.assertRaises(Invalid, VSignedString(key=key, required=True, 
                                                min_len=2, max_len=4).validate, 
                          *(VSignedString(key=key).sign('dummy'),))
        self.assertRaises(Invalid, VSignedString(key=key, 
                                                min_len=2, max_len=4).validate, 
                          *(VSignedString(key=key).sign('dummy'),))

        self.assertEqual('dummy', VSignedString(key=key).validate(VSignedString(key=key).sign('dummy')))
        self.assertEqual(dummy.content, VSignedObject(key=key).validate(VSignedObject(key=key).sign(dummy)).content)