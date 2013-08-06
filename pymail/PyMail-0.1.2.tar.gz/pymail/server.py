'''
Module server
-------------

Contains the Server class which is effectively the 'Application' object.
'''

from . import smtp, spooler, configuration
from .debug import D
from gettext import gettext as _
import argparse
import eventlet
import eventlet.debug
import grp
import logging
import logging.config
import os
import pkg_resources
import pwd
import socket
import sys

DEFAULT_CONFIG_FILE = '/etc/pymail/config'
DEFAULT_INTERFACE = '0.0.0.0'
DEFAULT_PORT = 25
DEFAULT_USER = 'mail'
DEFAULT_GROUP = 'mail'
DEFAULT_PIDFILE = '/var/run/pymail.run' # TODO: use it
GREENPOOL_SIZE = 1000

class InitError(RuntimeError):
    '''
    Initialization error
    '''

class DetachError(RuntimeError):
    '''
    Error trying to detach process
    '''

class Server(object):
    '''
    The Server class is the application singleton

    Synopsis::

        import server
        import sys
        srv = server.Server(sys.argv)
        srv.start()
    '''
    def __init__(self, args):
        '''
        Create a Server object

        :param list arguments: command line arguments without command (arg 0)
        '''
        #: Logger
        self.log = logging.getLogger('pymail.server.Server')
        #: Arguments (argparse.ArgumentParser)
        argParser = argparse.ArgumentParser(
            description=_('A mail (SMTP) server')
        )
        argParser.add_argument('-c', '--config', action='store', help=_('Specify configuration file to use'))
        argParser.add_argument('-d', '--no-detach', action='store_true', help=_('Do not detach from terminal'))
        self.arguments = argParser.parse_args(args)
        #: Path to configuration file from command line argument --config <path-to-configfile>
        self.configFile = \
            self.arguments.config or \
            DEFAULT_CONFIG_FILE or \
            pkg_resources.resource_filename(__name__, 'etc/pymail')
        try:
            self.config = configuration.Configuration(self.configFile)
        except IOError as e:
            raise InitError('Could not open config file - %s' % str(e))
        #: Pid file for detecting double runs
        self.pidFile = self.config('pidfile', DEFAULT_PIDFILE)
        #: Username to change to
        self.user = self.config('user', DEFAULT_USER)
        #: Groupname to change to
        self.group = self.config('group', DEFAULT_GROUP)
        #: Spooler object
        self.spooler = None

    def start(self):
        '''
        Start all servers

        For every subsection in the ``server`` section a greenlet is spawned which creates an `smtp.Smtp` object and perpetually
        calls its `start()` method in order to accept connections.
        '''
        greens = eventlet.GreenPool(GREENPOOL_SIZE)
        if self.config.has('servers'):
            conf = self.config.servers
            if conf:
                for c in conf._.itervalues():
                    if not c:
                        c = {}
                    interface = c.get('interface', DEFAULT_INTERFACE)
                    port = c.get('port', DEFAULT_PORT)
                    # The listener needs to be created here and now. Doing it in the greenlet is not possible because at the
                    # time it has a chance to run we already have switched uid, preventing opening privileged ports.
                    try:
                        listener = eventlet.listen((interface, port))
                    except socket.error as e:
                        sys.stderr.write('Cannot open port %d on %s: %s\n' % (port, interface, e))
                        continue
                    greens.spawn_n(self.startConnection, listener, configuration.DictMapper(c))
        if os.name == 'posix':
            try:
                pw = pwd.getpwnam(self.user)
                uid = pw.pw_uid
                gid = pw.pw_gid
            except KeyError:
                pass
            try:
                gid = grp.getgrnam(self.group).gr_gid
            except KeyError:
                pass
            os.umask(07)
            os.setgid(gid)
            self.prepareFile(self.config.logging.handlers.default.filename, -1, gid)
            self.prepareFile(os.path.dirname(self.config.spoolfile) + '/', -1, gid)
            self.spooler = spooler.Spooler(self.config)
            # Drop privileges ======================================
            os.setuid(uid)
            if not self.arguments.no_detach:
                detach()
            self._start2(greens)
        else:
            self.spooler = spooler.Spooler(self.config)
            self._start2(greens)

    def _start2(self, greens):
        '''
        Phase two of start()

        :param eventlet.GreenPool greens:
        '''
        logging.config.dictConfig(self.config.dict('logging'))
        self.log = logging.getLogger('pymail')
        self.log.info('PyMail started')
        greens.spawn_n(self.spooler.cron)
        greens.waitall()

    def startConnection(self, listener, config):
        '''
        Start a connection

        :param eventlet.green.socket listener:
        :param DictMapper config: corresponding ``servers`` subsection
        '''
        self.log.info(
            'startConnection, listener=%s: %s',
            listener,
            ', '.join(['%s=%s' % (k, v) for k, v in list(config._.iteritems())])
        )
        session = smtp.Smtp(self, listener, config)
        while True:
            session.start()

    def prepareFile(self, path, uid, gid):
        '''
        Prepares access to a filename specified by a complete path

        :param string path:
        :param int uid: -1 means do not check or change uid
        :param int gid: -1 means do not check or change gid

        Creates a filename and the path of directories to it
        '''
        dirname = os.path.dirname(path)
        filename = os.path.basename(path)
        try:
            os.makedirs(dirname, 0770)
            self.log.info('Created directory %s', dirname)
        except OSError:
            pass
        if not os.path.exists(path) and filename:
            file(path, 'a')
            self.log.info('Created file %s', path)
        if gid != -1 and os.stat(path).st_gid != gid or uid != -1 and os.stat(path).st_uid != uid:
            os.chown(path, uid, gid)
            self.log.info('Done os.chown(%s, %d, %d)', path, uid, gid)
            os.chmod(path, 0660)
            self.log.info('Done os.chmod(%s, 0660)', path)

def detach():
    '''
    Detach from terminal
    '''
    def forkAndExit(error_message):
        '''
        Fork and exit
        '''
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, exc:
            exc_errno = exc.errno
            exc_strerror = exc.strerror
            raise DetachError("%s: [%d] %s" % (error_message, exc_errno, exc_strerror))
    forkAndExit(error_message="Failed first fork")
    os.setsid()
    forkAndExit(error_message="Failed second fork")
