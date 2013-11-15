#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

from formv.validators.base import VBase
from formv.validators.strings import VString
from formv.exception import Invalid
from formv.utils import empty, extract_text as _
from formv.utils.encoding import crypt

__all__ = ('VEncoded','VEncodedPair',)

class VEncoded(VString):
    def __init__(self, cost=2**12, **kw):
        VString.__init__(self, **kw)
        self.cost = cost
    
    def _validate(self, value):
        value = VString._validate(self, value)
        return crypt(value, cost=self.cost)


class VEncodedPair(VBase):
    """ chained validator, e.g. (user, password) pair """
    def __init__(self, required_field, required_label, 
                 available_field, cost=2**12, **kw):
        VBase.__init__(self, **kw)
        self.required_field = required_field
        self.available_field = available_field
        self.required_label = required_label
        self.cost = cost
    
    def _validate(self, form):
        self.messages.update({'invalid': _('You must provide a value for "%(required)s"')})
        a = form.get(self.available_field)
        r = form.get(self.required_field)
        if empty(r) and a:
            raise Invalid(self.message('invalid', required=self.required_label), form)        
        if r and a:
            r = crypt((r + a), cost=self.cost)
        return r