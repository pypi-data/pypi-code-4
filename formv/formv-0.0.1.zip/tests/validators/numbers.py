#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from formv.exception import Invalid
from formv.validators.numbers import *

class Test(unittest.TestCase):
    def test(self):        
        self.assertEqual(1, VInteger(min_val=0, max_val=10).validate(1))
        self.assertEqual(0, VInteger().validate(.9))
        self.assertEqual(1, VInteger().validate(1.0))
        self.assertRaises(Invalid, VInteger().validate, *('dummy',))
        
        self.assertEqual(1, VFloat(min_val=0, max_val=10).validate(1))
        self.assertEqual(.9, VFloat().validate(.9))
        self.assertEqual(1, VFloat().validate(1.0))
        self.assertRaises(Invalid, VFloat().validate, *('dummy',))

        self.assertEqual(1, VNumber(min_val=0, max_val=10).validate(1))
        self.assertEqual(.9, VNumber().validate(.9))
        self.assertEqual(1, VNumber().validate(1.0))
        self.assertRaises(Invalid, VNumber().validate, *('dummy',))