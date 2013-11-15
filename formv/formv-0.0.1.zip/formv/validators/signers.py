#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import base64, hmac
from hashlib import sha256
from formv.validators.base import VBase
from formv.validators.strings import VString
from formv.exception import Invalid
from formv.utils.encoding import decode, encode, sign
from formv.utils import extract_text as _
try:
    import cPickle as pickle
except ImportError:
    import pickle

__all__ = ('VSignedObject','VSignedString',)

class VSignedString(VString):
    def __init__(self, key, **kw):
        VString.__init__(self, **kw)
        self.key = encode(key)

    def _validate(self, value):        
        value = VString._validate(self, value)
        self.messages.update({'invalid': _('Invalid signed string')})

        decoded = base64.b64decode(encode(value))
        value, signature = decoded[:-64], decoded[-64:]
        hashed = hmac.new(self.key, sign(value, self.key), sha256).hexdigest()
        if encode(hashed) != signature:
            raise Invalid(self.message('invalid'), value)
        return decode(value)
    
    def sign(self, value):
        if value:
            hashed = hmac.new(self.key, sign(value, self.key), sha256).hexdigest()
            return base64.b64encode(encode(value + hashed)) 
    

class VSignedObject(VBase):
    def __init__(self, key, **kw):
        VBase.__init__(self, **kw)
        self.key = encode(key)
    
    def _validate(self, value):
        self.messages.update({'invalid': _('Invalid signed object')})
        
        decoded = base64.b64decode(encode(value))
        pickled, signature = decoded[:-64], decoded[-64:]        
        hashed = hmac.new(self.key, sign(pickled, self.key), sha256).hexdigest()
        if encode(hashed) != signature:
            raise Invalid(self.message('invalid'), value)
        try:
            value = pickle.loads(pickled)
        except Exception as e:
            raise Invalid(e, value)        
        return value        
    
    def sign(self, value):
        if value:
            pickled = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
            hashed = hmac.new(self.key, sign(pickled, self.key), sha256).hexdigest()
            return base64.b64encode(pickled + encode(hashed)) 

