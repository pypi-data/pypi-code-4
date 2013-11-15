#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from datetime import datetime
from formv.exception import Invalid
from formv.validators import *

class Test(unittest.TestCase):
    def test(self):                
        self.assertIsNone(VAny(VInteger(), VString()).validate(None))
        self.assertIsNone(VPipe(VInteger(), VString()).validate(None))
        
        self.assertEqual(10, VAny(VInteger(), VString()).validate(10))
        self.assertEqual('10', VAny(VString(), VInteger()).validate(10))
        
        self.assertEqual('10', VPipe(VInteger(), VString()).validate(10))
        self.assertEqual(10, VPipe(VString(), VInteger()).validate(10))

        self.assertEqual(datetime(2012, 11, 8), VAny(VToDate(date_format='%d/%m/%Y'), 
                                                    VDate(today_or_after=False)).validate('08/11/2012'))

        self.assertEqual(datetime(2012, 11, 8), VAny(VToDate(date_format='%d/%m/%Y'), 
                                                    VDate(today_or_after=True)).validate('08/11/2012'))

        self.assertEqual(datetime(2012, 11, 8), VPipe(VToDate(date_format='%d/%m/%Y'), 
                                                     VDate(today_or_after=False)).validate('08/11/2012'))

        self.assertRaises(Invalid, VPipe(VToDate(date_format='%d/%m/%Y'), 
                                        VDate(today_or_after=True)).validate, *('08/11/2012',))