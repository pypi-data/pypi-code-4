#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from datetime import date, datetime
from formv.exception import Invalid
from formv.validators.dates import *

class Test(unittest.TestCase):
    def test(self):
        self.assertIsNone(VDate().validate(None))
        self.assertIsNone(VToDate().validate(None))

        for d in (date(1970, 1, 2), datetime(1970, 1, 2)): #January 2nd, 1970
            self.assertEqual(d, VDate().validate(d))
            self.assertEqual(d, VDate(earliest_date=d).validate(d))
            self.assertEqual(d, VDate(latest_date=d).validate(d))
            self.assertRaises(Invalid, VDate(after_now=True).validate, *(d,))        
            self.assertRaises(Invalid, VDate(today_or_after=True).validate, *(d,))
            self.assertEqual(50400, VDate(return_timestamp=True).validate(d))            
        now = datetime.now()
        self.assertEqual(now, VDate(today_or_after=True).validate(now))
        self.assertEqual(datetime(1970, 1, 2), VToDate(date_format='%d/%m/%Y').validate('02/01/1970'))
        self.assertEqual(datetime(1970, 1, 2), VToDate(date_format='%d/%m/%Y').validate('02/01/1970'))
        
        self.assertEqual('23:00:50', VTime().validate('230050'))
        self.assertEqual('23:00', VTime().validate('2300'))        
        self.assertEqual('23:00:50', VTime().validate('23:00:50'))
        self.assertEqual('23:10', VTime().validate('23:10'))        
        self.assertEqual('23:00:50', VTime().validate('23-00-50'))
        self.assertEqual('23:10', VTime().validate('23-10'))

        self.assertRaises(Invalid, VTime().validate, *('23/10',))                
        self.assertRaises(Invalid, VTime().validate, *('25:10',))
        self.assertRaises(Invalid, VTime().validate, *('20:70:00',))