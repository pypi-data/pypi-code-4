#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import formv
from formv.exception import Invalid
from formv.utils import empty, extract_text as _

__all__ = ('VBase','VBool','VConstant','VEmpty',
           'VLength','VList','VRange','VSet',)

class VBase(object):
    messages = {}
    
    def __init__(self, required=False, strip=True):
        self.required = required
        self.strip = strip
    
    def validate(self, value):
        self.messages.update({'required': _('Please enter a value')})
        
        if hasattr(value, 'mixed'):
            value = value.mixed()
        
        if self.strip:
            if hasattr(value, 'strip'):
                value = value.strip()

        if hasattr(value, 'mixed'):
            value = value.mixed()
       
        if empty(value):
            if self.required:
                raise Invalid(self.message('required'), value)
            else:
                return None
        return self._validate(value)
    
    def _validate(self, value):
        return value
    
    def message(self, msg, **kw):
        try:
            return formv.translate(self.messages[msg]) % kw
        except KeyError:
            m = 'Translation not found for %r=%r %% %r'             
            raise KeyError(m % (msg, self.messages.get(msg), kw))


class VConstant(VBase):
    def __init__(self, ct, **kw):
        VBase.__init__(self, **kw)
        self.ct = ct

    def _validate(self, value):
        return self.ct    

    
class VBool(VBase):
    def _validate(self, value):
        return bool(value)


class VEmpty(VBase):
    def _validate(self, value):
        self.messages.update({'invalid': _('You cannot enter a value here')})
        if not empty(value):
            raise Invalid(self.message('invalid'), value)
        return value
    
    
class VLength(VBase):
    def __init__(self, min_len=None, max_len=None, **kw):        
        VBase.__init__(self, **kw)
        self.min_len = int(min_len) if min_len is not None else None
        self.max_len = int(max_len) if max_len is not None else None

    def _validate(self, value):
        self.messages.update({
            'min_len': _('Enter a value %(min_len)i characters long or more'),
            'max_len': _('Enter a value not more than %(max_len)i characters long'),
            'no_length': _('Invalid value, length can\'t be determined')
        })
        try:
            if self.min_len is not None:
                if len(value) < self.min_len:
                    msg = self.message('min_len', min_len=self.min_len)
                    raise Invalid(msg, value)
            if self.max_len is not None:
                if len(value) > self.max_len:
                    msg = self.message('max_len', max_len=self.max_len)
                    raise Invalid(msg, value)
            return value
        except TypeError:        
            raise Invalid(self.message('no_length'), value)


class VRange(VBase):    
    def __init__(self, min_val=None, max_val=None, **kw):
        VBase.__init__(self, **kw)
        self.min_val = min_val
        self.max_val = max_val
        
    def _validate(self, value):
        self.messages.update({
            'min_val': _('Please enter a value that is %(min_val)s or greater'),
            'max_val': _('Please enter a value that is %(max_val)s or smaller')
        })        

        if self.min_val is not None:
            if value < self.min_val:
                msg = self.message('min_val', min_val=self.min_val)
                raise Invalid(msg, value, )
        if self.max_val is not None:
            if value > self.max_val:
                msg = self.message('max_val', max_val=self.max_val)
                raise Invalid(msg, value)
        return value
    

class VList(VBase):
    def _validate(self, value):
        if isinstance(value, list):
            return value
        elif isinstance(value, (set, tuple)):
            return list(value)
        else:
            return [value]


class VSet(VBase):
    def _validate(self, value):
        if isinstance(value, set):
            return value
        elif isinstance(value, (list, tuple)):
            return set(value)
        else:
            return set([value])

