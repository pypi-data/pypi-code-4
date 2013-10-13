'''
Created on Oct 1, 2013

@author: "Colin Manning"
'''

import os
import socket
from JDs import JDs

class WebService(object):
    '''
    Provide simple web service access to the PrintFlow data stores and files
    '''

    configData = None
    ready = False
    theSocket = None

    def __init__(self, configFile):
        '''
        Constructor
        '''
        self.ready = True
    
    def is_ready(self):
        return self.ready
    
    def start(self):
        self.theSocket = socket()
        
    def stop(self):
        self.theSocket.close()