#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import formv
from formv.configuration import BaseCountry
from formv.utils import dict_object
from formv.utils.encoding import encode


class Multipart(object):
    def empty(self, fieldname):
        m = ('\r\nContent-Disposition: form-data; name="%(fieldname)s"\r\n'
             '\r\n')
        return encode(m % {'fieldname':fieldname})

    def field(self, fieldname, fieldcontent):
        m = ('\r\nContent-Disposition: form-data; name="%(fieldname)s"\r\n'
             '\r\n'
             '%(fieldcontent)s\r\n')
        return encode(m % {'fieldname':fieldname, 'fieldcontent':fieldcontent})

    def file(self, fieldname, filename, content_type='application/octet-stream'):
        m = encode((
            '\r\nContent-Disposition: form-data; name="%(fieldname)s"; filename="%(filename)s"\r\n'
            'Content-type: %(content_type)s\r\n'
            '\r\n') % {'fieldname':fieldname, 'filename':filename, 'content_type':content_type})
    
        f = open(filename, 'rb')   
        try:
            return m + f.read() + b'\r\n\r\n' 
        finally:
            f.close() 

multipart = Multipart()


class Country(BaseCountry):
    """ test mock-up """
    def __init__(self, code):
        BaseCountry.__init__(self)
        self.code = 'USA'
        self.name = 'U.S.A.'
        self.names = ('U.S.A.', 'USA', 'U.S.', 'US', 'United States of America')
        self.languages = ('ENG',)
        self.currencies = ('USD',)
        self.phone_code = '+1'
        self.formats.phone = ("(###) ###-####", "1 (###) ###-####",
                              "+1 (###) ###-####", "1-###-###-####", 
                              "1-###-###-####", "+1-###-###-####",)
        self.formats.postcode = ("####", '#####',)
        self.postcodes = self.Postcodes(country=self.code)        
        self.states = self.States(country=self.code)
        
    class Postcodes(BaseCountry.Postcodes):
        def get(self, postcode):
            if self.country == 'USA' and postcode == '99501':
                return ('61.216799', '-149.87828')

        def items(self):
            if self.country == 'USA': 
                for k in ('99501',):
                    yield (k, ('61.216799', '-149.87828'))
        
        iteritems = items
        
    class States(BaseCountry.States):
        def get(self, state):
            if self.country == 'USA' and state == 'AK':
                return dict_object({'code':'AK', 
                                    'name':'Alaska', 
                                    'names': ('AK', 'Alaska'),
                                    'postcodes': self.Postcodes(country=self.country, state=state)
                                    })
        
        def items(self):
            if self.country == 'USA':
                for state in ('AK',):
                    yield (state, dict_object({'code':'AK', 
                                               'name':'Alaska', 
                                               'names': ('AK', 'Alaska'),
                                               'postcodes': self.Postcodes(country=self.country, state=state)
                                               }))
        
        iteritems = items    
        
        class Postcodes(BaseCountry.States.Postcodes):
            def get(self, postcode):
                if self.country == 'USA' and self.state == 'AK' and postcode == '99501':
                    return ('61.216799', '-149.87828')
    
            def items(self, ):
                if self.country == 'USA' and self.state == 'AK':
                    for k in ('99501',):
                        yield (k, ('61.216799', '-149.87828'))
                
            iteritems = items        