'''
Contains handlers for SMTP authentication.
'''

import base64

class BaseAuthenticator(object):
    '''
    Base class for authenticators
    '''

    def __init__(self, session):
        '''
        Create authenticator

        :param Smtp session:
        '''
        self.session = session

    def start(self, _words): # pylint: disable=R0201
        '''
        Start authentication

        :param string-list words: parameters from AUTH command
        '''
        return True

    def handleLine(self, _line): # pylint: disable=R0201
        '''
        Get a line from session

        :param string line:
        '''
        return True

# Probably needs its own module
class PlainAuthenticator(BaseAuthenticator):
    '''
    Handler for PLAIN authentication
    '''

    def __init__(self, session):
        '''
        Create PlainAuthenticator object

        :param Smtp session: Smtp session object
        '''
        super(PlainAuthenticator, self).__init__(session)

    def start(self, words):
        assert words[1].upper() == 'PLAIN'
        username, password = base64.decodestring(words[2]).split('\0')[1:]
        self.session.authenticate(username, password)
        return True
