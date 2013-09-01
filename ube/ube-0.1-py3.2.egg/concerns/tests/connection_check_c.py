'''
Created on Nov 6, 2012

@author: Nicklas Boerjesson
'''
from ube.concerns.connection import connection_c

'''This is a dummy module, only to be able to do testing without having unittest
    instantiate too early '''

@connection_c
class connection_check_class(object):
    _dal = None 
    
    def connection_check(self, _sql):
        self._dal.execute(_sql)  


