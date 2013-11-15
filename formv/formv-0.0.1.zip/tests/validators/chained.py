#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest
from formv.exception import Invalid
from formv.validators.chained import *

class Test(unittest.TestCase):
    def test_base(self):   
        fields = ('email', 'phone', 'fax')             
        value = {'email':None, 'phone':None, 'fax':None}        
        self.assertRaises(Invalid, VAnyField(fields, 'dummy').validate, *(value,))
        self.assertRaises(Invalid, VAllFields(fields, 'dummy').validate, *(value,))

        value = {'email':'dummy@dummy.com', 'phone':None, 'fax':None}        
        self.assertEqual(None, VAnyField(fields, 'dummy').validate(value))
        self.assertRaises(Invalid, VAllFields(fields, 'dummy').validate, *(value,))
        
        value = {'email':'dummy@dummy.com', 'phone':'+1 234 56789', 'fax':'+1 234 56789'}        
        self.assertEqual(None, VAnyField(fields, 'dummy').validate(value))
        self.assertEqual(None, VAllFields(fields, 'dummy').validate(value))
    
    def test_pair(self):
        value = {'phone':None, 'phone_type':None}  
        self.assertIsNone(VPair('phone_type', 'Phone Type', 'phone').validate(value,))      

        value = {'phone':None, 'phone_type':'mobile'}  
        self.assertEqual('mobile', VPair('phone_type', 'Phone Type', 'phone').validate(value,))      

        value = {'phone':'+1 234 56789', 'phone_type':'mobile'}  
        self.assertEqual('mobile', VPair('phone_type', 'Phone Type', 'phone').validate(value,))      
 
        value = {'phone':'+61 4234 6789', 'phone_type':None}  
        self.assertRaises(Invalid, VPair('phone_type', 'Phone Type', 'phone').validate, *(value,))      

    def test_postcode(self):
        value = {'country':None, 'state':None, 'postcode':None}  
        self.assertIsNone(VCountryPostcode('country','postcode').validate(value))      
  
        value = {'country':None, 'postcode':'99501'}  
        self.assertIsNone(VCountryPostcode('country','postcode').validate(value))      
  
        value = {'country':'USA', 'postcode':None}  
        self.assertIsNone(VCountryPostcode('country','postcode').validate(value))      
  
        value = {'country':'USAx', 'postcode':'99501'}  
        self.assertIsNone(VCountryPostcode('country','postcode').validate(value))      
  
        value = {'country':'USA', 'postcode':'99501'}  
        self.assertTupleEqual((float('61.216799'), float('-149.87828')), 
                             VCountryPostcode('country','postcode').validate(value))      

        value = {'country':'USA', 'postcode':'dummy'}  
        self.assertRaises(Invalid, VCountryPostcode('country','postcode').validate, *(value,))      

        value = {'country':'USA', 'state':'AK', 'postcode':'99501'}
        self.assertTupleEqual((float('61.216799'), float('-149.87828')), 
                             VCountryStatePostcode('country','state','postcode').validate(value))      

    def test_postcode_format(self):
        value = {'country':'USA', 'postcode':'99501'}  
        self.assertEqual('99501', VPostcodeFormat('country','postcode').validate(value))      
      
    def test_phone_format(self):
        value = {'country':'USA', 'phone':'+1-234-567-8901'}  
        self.assertEqual('+1-234-567-8901', VPhoneFormat('country','phone').validate(value))      

        value = {'country':'USA', 'phone':'(123) 456-7890'}  
        self.assertEqual('(123) 456-7890', VPhoneFormat('country','phone').validate(value))      

        value = {'country':'USA', 'phone':'+1 2 3456 789'}  
        self.assertRaises(Invalid, VPhoneFormat('country','phone').validate, *(value,))      

        value = {'country':'USA', 'phone':'2 345 6789'}  
        self.assertRaises(Invalid, VPhoneFormat('country','phone').validate, *(value,))     
         
        value = {'country':'USA', 'phone':'2 345 6abc'}  
        self.assertRaises(Invalid, VPhoneFormat('country','phone').validate, *(value,))     

    def test_state(self):
        value = {'country':None, 'state':None}  
        self.assertIsNone(VState('country','state', mode='by-name').validate(value))      

        value = {'country':None, 'state':'AK'}  
        self.assertIsNone(VState('country','state', mode='by-name').validate(value))      
 
        value = {'country':'USA', 'state':None}  
        self.assertIsNone(VState('country','state', mode='by-name').validate(value))      
 
        value = {'country':'USAx', 'state':'AK'}  
        self.assertIsNone(VState('country','state', mode='by-name').validate(value))      
 
        value = {'country':'USA', 'state':'Alaska'}  
        self.assertEqual('AK', VState('country','state', mode='by-name').validate(value))      

        value = {'country':'USA', 'state':'dummy'}  
        self.assertRaises(Invalid, VState('country','state', mode='by-name').validate, *(value,))      

        value = {'country':'USA', 'state':'AK'}  
        self.assertEqual('AK', VState('country','state', mode='by-code').validate(value))      
    
    def test_currency(self):
        value = {'country':None, 'currency':None}  
        self.assertIsNone(VCurrency('country','currency', mode='by-name').validate(value))      
 
        value = {'country':None, 'currency':'USD'}  
        self.assertIsNone(VCurrency('country','currency', mode='by-name').validate(value))      
  
        value = {'country':'USA', 'currency':None}  
        self.assertIsNone(VCurrency('country','currency', mode='by-name').validate(value))      
  
        value = {'country':'USAx', 'currency':'USD'}  
        self.assertIsNone(VCurrency('country','currency', mode='by-name').validate(value))      
 
        value = {'country':'USA', 'currency':'$'}  
        self.assertEqual('USD', VCurrency('country','currency', mode='by-name').validate(value))      
 
        value = {'country':'USA', 'currency':'dummy'}  
        self.assertRaises(Invalid, VCurrency('country','currency', mode='by-name').validate, *(value,))

        value = {'country':'USA', 'currency':'USD'}  
        self.assertEqual('USD', VCurrency('country','currency', mode='by-code').validate(value))      

        value = {'country':'USA', 'currency':'American Dollar'}  
        self.assertEqual('USD', VCurrency('country','currency', mode='by-name').validate(value))      
       
    def test_language(self):
        value = {'country':None, 'language':None}  
        self.assertIsNone(VLanguage('country','language', mode='by-name').validate(value))      
 
        value = {'country':None, 'language':'ENG'}  
        self.assertIsNone(VLanguage('country','language', mode='by-name').validate(value))      

        value = {'country':'USA', 'language':'ENGLISH'}  
        self.assertEqual('ENG', VLanguage('country','language', mode='by-name').validate(value))      

        value = {'country':'USA', 'language':'dummy'}  
        self.assertRaises(Invalid, VLanguage('country','language', mode='by-name').validate, *(value,))      
    
    def test_creditcard(self):   
        # Test Credit Card Account Numbers   
        # https://www.paypalobjects.com/en_US/vhelp/paypalmanager_help/credit_card_numbers.htm      
        value = {'card_type':'VISA', 'card_number':'4012888888881881', 
                 'card_expiration':'10/2018', 'card_security_code':'321'}
        
        self.assertIsNone(VCreditCard(card_type_field='card_type', 
                                      card_number_field='card_number', 
                                      card_expiration_field='card_expiration', 
                                      card_security_code_field='card_security_code').validate(value))

        value['card_number'] = '4012888888881123'
        self.assertRaises(Invalid, 
                          VCreditCard(card_type_field='card_type', 
                                      card_number_field='card_number', 
                                      card_expiration_field='card_expiration', 
                                      card_security_code_field='card_security_code').validate, *(value,))

        value['card_type'] = 'AMEX'
        value['card_number'] = '378282246310005'
        value['card_security_code'] = '4321'
        self.assertIsNone(VCreditCard(card_type_field='card_type', 
                                      card_number_field='card_number', 
                                      card_expiration_field='card_expiration', 
                                      card_security_code_field='card_security_code').validate(value))

        value['card_number'] = '378282246310123'
        self.assertRaises(Invalid, 
                          VCreditCard(card_type_field='card_type', 
                                      card_number_field='card_number', 
                                      card_expiration_field='card_expiration', 
                                      card_security_code_field='card_security_code').validate, *(value,))

        value['card_type'] = 'DISCOVER'
        value['card_number'] = '6011000990139424'
        value['card_security_code'] = '321'
        self.assertIsNone(VCreditCard(card_type_field='card_type', 
                                      card_number_field='card_number', 
                                      card_expiration_field='card_expiration', 
                                      card_security_code_field='card_security_code').validate(value))

        value['card_number'] = '6011000990139123'
        self.assertRaises(Invalid, 
                          VCreditCard(card_type_field='card_type', 
                                      card_number_field='card_number', 
                                      card_expiration_field='card_expiration', 
                                      card_security_code_field='card_security_code').validate, *(value,))

        value['card_type'] = 'MasterCard'
        value['card_number'] = '5555555555554444'
        value['card_security_code'] = '321'
        self.assertIsNone(VCreditCard(card_type_field='card_type', 
                                      card_number_field='card_number', 
                                      card_expiration_field='card_expiration', 
                                      card_security_code_field='card_security_code').validate(value))

        value['card_number'] = '5555555555554123'
        self.assertRaises(Invalid, 
                          VCreditCard(card_type_field='card_type', 
                                      card_number_field='card_number', 
                                      card_expiration_field='card_expiration', 
                                      card_security_code_field='card_security_code').validate, *(value,))

        value['card_type'] = 'JCB'
        value['card_number'] = '3566002020360505'
        value['card_security_code'] = '321'
        self.assertIsNone(VCreditCard(card_type_field='card_type', 
                                      card_number_field='card_number', 
                                      card_expiration_field='card_expiration', 
                                      card_security_code_field='card_security_code').validate(value))

        value['card_number'] = '3566002020360123'
        self.assertRaises(Invalid, 
                          VCreditCard(card_type_field='card_type', 
                                      card_number_field='card_number', 
                                      card_expiration_field='card_expiration', 
                                      card_security_code_field='card_security_code').validate, *(value,))