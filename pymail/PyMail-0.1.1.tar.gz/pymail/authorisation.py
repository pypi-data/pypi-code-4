'''

This module contains the authorisation classes. They look up the user information from various sources.
'''

from debug import D

class Authorisation(object):
    '''
    Base class for authorisation classes
    '''
    def __init__(self, session, config):
        '''
        Create Authorisation object
        '''
        self.session = session
        self.config = config

    def authorize(self, _username, _password):
        '''
        Authorize user with password

        :param string username:
        :param string password:
        :return: True if authorized
        '''

class ConfigAuthorisation(Authorisation):
    '''
    Authorisation from ``users`` section in config file

    User accounts are defined in section ``authorisation.users``. A user definitions consists of the following entries:

    * username: The single-word username. There are no restrictions for the name at the moment
    * password: The single-word password.

    Any other entry is ignored.

    It should be common sense that this is not the proper place to define user accounts. Use this only for testing or if there
    are only handful of users.
    '''
    def __init__(self, session, config):
        super(ConfigAuthorisation, self).__init__(session, config)

    def authorize(self, username, password):
        return password == self.config.get(username)