'''
Created on Sep 6, 2012

@author: Nicklas Börjesson
'''
from ube.concerns.connection import connection

class permissions(object):
    """This decorator checks and manages permissions. (Unfinished)"""


    def __init__(self,params):
        """
        Constructor
        """
        pass
    @connection
    def check_object(self, _entityid, _sessionid, _typeguid, _connection = None):
        pass
        
        
        