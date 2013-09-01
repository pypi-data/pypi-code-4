'''
Created on May 8, 2010

@author: Nicklas Boerjesson
'''

#from suds.client import client
from ube.common.settings import UBPMSettings

class UBPMSession(object):
    '''
    The session class contains:
    * providing database connection(s).
    * security desciptors.
    * session information.
    '''
    
    global UnifiedBPMURI
    global AuthenticationServer
    global Username
    
    
    def New_Session(self, login, password):
        '''
        Get a new session from the authentication server.
        '''
        
        # Read credentials
        self.Username = UBPMSettings.Parser.get("credentials", "username")
        self.Password = UBPMSettings.Parser.get("credentials", "password")
        
        raise Exception('Invalid login')

    def __init__(self,settings):
        '''
        Constructor
        '''
        # Read system settings
        self.UnifiedBPMURI = settings.Parser.get("broker", "broker_server_base_URI")

        AuthURI = self.UnifiedBPMURI + '/services/authentication_soap.wsgi?wsdl'
        print ("Creating Session SOAP client, URL: " + AuthURI)
#        self.AuthenticationServer = client(AuthURI);
        print ("Done.")
        
        
        

    