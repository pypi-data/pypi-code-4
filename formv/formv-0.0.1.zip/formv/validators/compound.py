#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

from formv.exception import Invalid

__all__ = ('VAny','VPipe',)

class VCompound(object):
    def __init__(self, *args):        
        self.validators = args        
        
        
class VAny(VCompound):
    """ return the value of the first successful validator (any can succeed) """
    def validate(self, value):
        exc = None        
        for v in self.validators:
            try:
                return v.validate(value)
            except Invalid as e:
                exc = e
        if exc:
            raise exc


class VPipe(VCompound):
    """ return the value of the last validator (all must succeed) """    
    def validate(self, value):
        for v in self.validators:
            value = v.validate(value)
        return value