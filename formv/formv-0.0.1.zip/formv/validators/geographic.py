#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import formv
from formv.validators.base import VBase
from formv.validators.numbers import VFloat
from formv.exception import Invalid
from formv.utils import extract_text as _

__all__ = ('VCountry','VLatitude','VLongitude',)

# for other geographic validators see formv.validators.chained

class VLatitude(VFloat):
    def __init__(self, **kw):
        VFloat.__init__(self, min_val=-90, max_val=90, **kw)
    

class VLongitude(VFloat):
    def __init__(self, **kw):
        VFloat.__init__(self, min_val=-180, max_val=180, **kw)


class VCountry(VBase):
    def __init__(self, mode='by-code', **kw):
        VBase.__init__(self, **kw)
        assert mode in ('by-code','by-name')
        self.mode = mode        
    
    def _validate(self, value):
        self.messages.update({'invalid': _('Invalid country: %(country)s')})
        if self.mode == 'by-code':
            return self._by_code(value)
        if self.mode == 'by-name':
            return self._by_name(value)
        
    def _by_code(self, value):
        for country in formv.config.countries.values():
            if value.upper() == country.code.upper():
                return country.code
        raise Invalid(self.message('invalid', country=value), value)
                        
    def _by_name(self, value):
        for country in formv.config.countries.values():
            if value.upper() in [n.upper() for n in country.names]:
                return country.code
        raise Invalid(self.message('invalid', country=value), value)