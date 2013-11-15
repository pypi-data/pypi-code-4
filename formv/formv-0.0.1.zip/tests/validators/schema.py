#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from datetime import datetime
from formv.validators import *   
from formv.exception import Invalid

class Form(VSchema):
    
    fields = {        
        'first_name': VString(min_len=3, max_len=50),
        'last_name': VString(min_len=3, max_len=50),
        'email': VEmail(required=True),
        'postcode': VString(),
        'state': VString(),
        'country': VCountry(required=True, mode='by-name'),
        'currency': VString(),
        'price': VFloat(),
        'units': VInteger(),
        'pay_method': VString(),
        'phone': VString(),
        'phone_type': VString(),
        'fax': VString(),
        'last_change': VDate(today_or_after=True),
        'missing_field': VString(),  
        'username': VString(),
        'password': VPassword(special_chars=3),  
        'encoded': VEncoded(),
#         'form': VString()     
    }
    
    chains = {
        'contact': VAnyField(fields=('email', 'phone', 'fax'),
                             msg='Please provide some relevant, public contact details'), 
              
        'state': VState(country_field='country', 
                        state_field='state',
                        mode='by-name'),

        'currency': VCurrency(country_field='country', 
                              currency_field='currency',
                              mode='by-name'),
              
        'coordinates': VCountryPostcode(country_field='country', 
                                        postcode_field='postcode'),
              
        'phone_type': VPair(required_field='phone_type',
                            required_label='Phone type', 
                            available_field='phone'),

        'pay_method': VPair(required_field='pay_method',
                            required_label='Payment method', 
                            available_field='price'),
               
        'password': VEncodedPair(required_field='password',
                                 required_label='Password', 
                                 available_field='username')
    }

class Test(unittest.TestCase):    
    def setUp(self):
        self.web_form = {
            'first_name': 'John',
            'last_name': 'Smith',
            'email': 'dummy@dummy.com',
            'postcode': '99501',     
            'state': 'Alaska',  
            'country': 'U.S.A.',
            'currency': '$',
            'price': 500, 
            'units': 3,
            'pay_method': 'Cash',
            'phone': '+1 234 56789',
            'phone_type': 'Mobile',
            'fax': '+1 234 56789',
            'last_change': datetime.utcnow(),
            'extra_field': 'dummy',
            'username': 'dummy-username',
            'password': 'dummy-secret-password-1',      
            'encoded': 'dummy',   
        }
        
    def tearDown(self):
        self.web_form = {}
        
    def test(self):
        self.assertRaises(Invalid, Form().validate, *(self.web_form,))
        
        self.assertRaises(Invalid, Form(allow_missing_keys=True,).validate, *(self.web_form,)) 
        
        self.assertDictEqual(self.web_form, 
                             Form(allow_missing_keys=True,
                                  allow_extra_keys=True).validate(self.web_form))

        self.assertAlmostEqual(self.web_form, 
                               Form(allow_missing_keys=True,
                                    allow_extra_keys=True,
                                    replace_missing_key=True,).validate(self.web_form),
                               {'missing_field':None})
        
        self.assertAlmostEqual(self.web_form, 
                               Form(allow_missing_keys=True,
                                    allow_extra_keys=True,
                                    replace_missing_key=True,
                                    missing_key_value='dummy').validate(self.web_form),
                               {'missing_field':'dummy'})

        self.assertAlmostEqual(Form(allow_missing_keys=True,
                                    allow_extra_keys=True,
                                    replace_missing_key=True,
                                    missing_key_value='dummy').validate(self.web_form),
                               self.web_form,
                               {'extra_field':'dummy'})

