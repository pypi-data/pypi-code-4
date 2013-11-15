#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from formv.exception import Invalid
from formv.validators.strings import *
from formv.utils.encoding import decode, encode

class Test(unittest.TestCase):
    def test(self):
        self.assertIsNone(VString().validate(''))
        self.assertIsNone(VString().validate(None))
        self.assertEqual('dummy', VString().validate('dummy'))
        self.assertEqual(decode(encode('☻☺■¹€')), VString().validate(decode(encode('☻☺■¹€'))))
        self.assertEqual('dummy', VString(1, 10).validate('dummy'))
        self.assertRaises(Invalid, VString(1, 4).validate, *('dummy',))
        self.assertRaises(Invalid, VString(6, 10).validate, *('dummy',))
        self.assertEqual('DUMMY', VRegex(r'^[A-Z]+$').validate('DUMMY'))
        self.assertRaises(Invalid, VRegex(r'^[A-Z]+$').validate, *('dummy',))
        self.assertEqual('a-B_5', VText().validate('a-B_5',))
        self.assertRaises(Invalid, VText().validate, *('@dummy',))
        
        self.assertEqual('a@b.co', VEmail().validate('a@b.co'))
        self.assertEqual('a+a@b.co', VEmail().validate('a+a@b.co'))
        self.assertEqual('a+a@b.b.co', VEmail().validate('a+a@b.b.co'))
        self.assertEqual('a+a@b.b.co', VEmail().validate('a+a@b.b.co'))
        self.assertEqual('a+a@b.b1.co', VEmail().validate('a+a@b.b1.co'))
        
        self.assertRaises(Invalid, VEmail().validate, *('a@b',))
        self.assertRaises(Invalid, VEmail().validate, *('a@8.8.8.8',))
        self.assertRaises(Invalid, VEmail().validate, *('☺a@test.com',))
        self.assertRaises(Invalid, VEmail().validate, *('a@☺test.com',))
        self.assertRaises(Invalid, VEmail().validate, *('a@test.c☺m',))
        
        self.assertEqual('dummy', VPassword().validate('dummy'))
        self.assertEqual('$du@mmy#', VPassword(3).validate('$du@mmy#'))        
        self.assertEqual(decode(encode('☻☺■¹€')), VPassword(3).validate(decode(encode('☻☺■¹€'))))
        
        self.assertRaises(Invalid, VPassword().validate, *('',))
        self.assertRaises(Invalid, VPassword(3).validate, *('dummy',))
        self.assertRaises(Invalid, VPassword(3).validate, *('$dummy$',))
        self.assertRaises(Invalid, VPassword(special_chars=3, min_len=12, max_len=15).validate, *('$dum$my$',))
        self.assertRaises(Invalid, VPassword(special_chars=3, min_len=4, max_len=6).validate, *('$dum$my$',))        
       
        self.assertEqual('http://localhost', VURL().validate(decode(encode('http://localhost'))))
        self.assertEqual('http://dummy.com', VURL().validate('http://dummy.com'))
        self.assertEqual('http://xn--dummy-8l4b.com', VURL().validate(decode(encode('http://dum€my.com'))))
        self.assertEqual('ftp://xn--dummy-8l4b.com', VURL().validate(decode(encode('ftp://dum€my.com'))))
        self.assertRaises(Invalid, VURL(connect=True).validate, *(decode(encode('ftp://dum€my.com')),))
        self.assertRaises(Invalid, VURL().validate, *('dummy.com',))
        self.assertRaises(Invalid, VURL().validate, *(decode(encode('file://dum€my.com')),))
        
        # - http://useragentstring.com/
        ua = 'Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)'
        self.assertEqual(ua, VUserAgent().validate(ua))
        
        ua = 'Mozilla/4.0 (compatible; MSIE 6.0b; Windows NT 5.1)'
        self.assertRaises(Invalid, VUserAgent().validate, *(ua,))
