'''
Created on May 8, 2010

@author: Nicklas Boerjesson
'''

from configparser import SafeConfigParser

class user(object):
    global usernodeid, username, password
    
     

class users(object):
    global Parser
    
    '''
    This class is responsible for reading settings from the ini-files and holding them in memory.
    '''
    
    def reload(self,filename):
        self.Parser.read(filename)
    
    def __init__(self, filename):
        '''
        Constructor
        '''
        self.Parser = SafeConfigParser()
        if (filename != ''):
            # TODO: Add better config support.
            self.reload(filename)