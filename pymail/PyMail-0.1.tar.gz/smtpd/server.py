'''
Module server
-------------

Contains the Server class which is effectively the 'Application' object.
'''

import argparse
from gettext import gettext as _
from debug import D
import eventlet
import eventlet.debug
import configuration
import smtp
import spooler

DEFAULT_CONFIG_FILE = '/etc/pymail'

class InitError(RuntimeError):
    '''
    Initialization error
    '''
    def __init__(self, message):
        '''
        Create InitError object
        
        :param string message: message string
        '''
        super(InitError, self).__init__(message)

class Server(object):
    '''
    The Server class is the application singleton
    '''
    def __init__(self, args):
        '''
        Create a Server object
        
        If an arguments object is supplied, it is used to influence the initialisation.
        
        :param argparse.ArgumentParser arguments: arguments
        '''
        #: Arguments (argparse.ArgumentParser)
        argParser = argparse.ArgumentParser(
            description=_('A mail (SMTP) server')
        )
        argParser.add_argument('-c', '--config', action='store', help=_('Specify configuration file to use'))
        self.arguments = argParser.parse_args(args)
        #: Configuration (dict) from command line argument --config <path-to-configfile>
        self.configFile = self.arguments.config or DEFAULT_CONFIG_FILE
        try:
            self.config = configuration.Configuration(self.configFile)
        except IOError as e:
            raise InitError('Could not open config file - %s' % str(e))
        self.spooler = spooler.Spooler(self.config)

    def start(self):
        '''
        Start the server
        '''
        #eventlet.debug.hub_blocking_detection(True)
        greens = eventlet.GreenPool() #TODO: Pool size? Configurable?
        if self.config.has('servers'):
            conf = self.config.servers
            for s in conf._.iterkeys():
                greens.spawn_n(self.startConnection, configuration.DictMapper(conf._[s]))
        greens.spawn_n(self.spooler.cron)
        greens.waitall()

    def startConnection(self, config):
        '''
        Start a connection

        :param DictMapper config: configuration for connection
        '''
        D('startConnection: ', ', '.join(['%s=%s' % (k, v) for k, v in list(config._.iteritems())]))
        session = smtp.Smtp(self, config)
        while True:
            session.start()