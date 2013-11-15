#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from formv.exception import Invalid
from formv.validators.base import *

class Test(unittest.TestCase):
    def test(self):
        self.assertIsNone(VBase().validate(None))
        self.assertIsNone(VBase().validate(''))
        self.assertIsNone(VBase().validate('    '))
        self.assertIsNone(VConstant(ct=None).validate(None))
        self.assertFalse(VBool().validate(None))
        self.assertIsNone(VEmpty().validate(None))
        self.assertIsNone(VLength().validate(None))
        self.assertIsNone(VRange().validate(None))        
        self.assertIsNone(VList().validate(None))
        self.assertIsNone(VSet().validate(None))        
       
        self.assertEqual('abc', VBase(required=True).validate('  abc'))
        self.assertRaises(Invalid, VBase(required=True).validate, *('    ',))
        self.assertRaises(Invalid, VBase(required=True).validate, *(None,))

        self.assertFalse(VBool().validate(0))
        self.assertTrue(VBool().validate(1)) 

        self.assertEqual('ct', VConstant(ct='ct').validate('dummy')) 

        self.assertIsNone(VEmpty().validate('')) 
        self.assertIsNone(VEmpty().validate(None))
        self.assertRaises(Invalid, VEmpty().validate, *('dummy',))
        
        self.assertEqual(3, VRange(1, 10).validate(3))
        self.assertRaises(Invalid, VRange(1, 10).validate, *(0,))
        self.assertRaises(Invalid, VRange(1, 10).validate, *(11,))        

        self.assertEqual('dummy', VLength(1, 10).validate('dummy'))
        self.assertRaises(Invalid, VLength(1, 4).validate, *('dummy',))
        self.assertRaises(Invalid, VLength(6, 10).validate, *('dummy',))        

        self.assertEqual(set([1,2,3]) ^ set(VList().validate([1,2,3])), set())
        self.assertEqual(set([1,2,3]) ^ set(VList().validate((1,2,3))), set())
        self.assertEqual(set([1,2,3]) ^ set(VList().validate(set([1,2,3]))), set())
    
        self.assertEqual(set([1,2,3]) ^ VSet().validate([1,2,3,3]), set())
        self.assertEqual(set([1,2,3]) ^ VSet().validate((1,2,3,3)), set())
        self.assertEqual(set([1,2,3]) ^ VSet().validate(set([1,2,3,3])), set())