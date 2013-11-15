#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from formv.exception import Invalid
from formv.validators.geographic import *

class Test(unittest.TestCase):
    def test(self):                
        self.assertEqual(-45, VLatitude().validate(-45))
        self.assertRaises(Invalid, VLatitude().validate, *(300,))

        self.assertEqual(-165, VLongitude().validate(-165))
        self.assertRaises(Invalid, VLongitude().validate, *(300,))
        
        self.assertEqual('USA', VCountry(mode='by-code').validate('USA'))
        self.assertEqual('USA', VCountry(mode='by-code').validate('usa'))
        self.assertEqual('USA', VCountry(mode='by-name').validate('U.S.'))
        self.assertEqual('USA', VCountry(mode='by-name').validate('United States of America'))
        self.assertRaises(Invalid, VCountry().validate, *('dummy',))