'''
This module contains the Smtp class which handles SMTP connections
'''

from . import authenticator, authorisation
from .debug import softAssert
from gettext import gettext as _
import cPickle
import datetime
import eventlet
import logging
import re
import textwrap
import uuid
import socket
import email
from pymail import spooler

class Smtp(object):
    '''
    Handle incoming SMTP protocol
    '''

    #: Message catalog
    messages = {
        214: 'You are on your own',
        220: '%s %s ESMTP Service ready', # address, description
        221: '%s Service closing transmission channel', # address
        235: 'OK, go ahead',
        250: '%s', # some text
        354: 'Start spreading the news',
        421: '%s Service not available, closing transmission channel', #address
        450: 'Requested mail action not taken: mailbox unavailable',
        451: 'Requested action aborted: local error in processing',
        452: 'Requested action not taken: insufficient system storage',
        500: 'Syntax error',
        501: 'Syntax error in parameters or arguments',
        502: 'Command not implemented',
        503: 'Bad sequence of commands',
        504: 'Command parameter not implemented',
        535: 'Authentication failed',
        550: 'Requested action not taken: mailbox unavailable',
        551: 'User not local; please try %s', #address
        552: 'Requested mail action aborted: exceeded storage allocation',
        553: 'Requested action not taken: mailbox name not allowed',
        554: 'Transaction failed'
    }
    #: Regular expression for parsing mail addresses like John Doe<j.doe@somewhere.net>
    mailAddressRe = re.compile(r'[^<]*\<\s*([^>]*)\s*\>.*')
    #: Registry of authenticator classes
    authenticators = {
        'PLAIN': authenticator.PlainAuthenticator
    }
    #: Registry of authorizers
    authorizers = {
        'users': authorisation.ConfigAuthorisation
    }
    #: Text wrapper: splits line after 78 characters and indents subsequent lines
    wrapper = textwrap.TextWrapper(subsequent_indent='  ', width=78)

    def __init__(self, server_, listener, config):
        '''
        Create a Smtp object

        :param Server server_: server object
        :param dict config: config name in ``servers`` section
        '''
        #: Message ID
        self.messageId = None
        #: Logger
        self.log = logging.getLogger('pymail.smtp.Smtp')
        #: Server instance
        self.server = server_
        #: Config section (within *servers*)
        self.config = config
        #: Listener
        self.listener = listener
        #: IP
        self.address = None
        #: Network socket
        self.socket = None
        #: Network socket turned into file handle
        self.sockfile = None
        defaultDescription = self.server.config('description', 'PyMail') # TODO: add version in default
        #: Server description
        self.description = self.config('description', defaultDescription)
        #: Advertised server address (domain or IP)
        self.advertisedAddress = None
        #: State (method)
        self.state = None
        #: Client address
        self.client = None
        #: Sender domain
        self.mailFrom = None
        #: Destination list
        self.rcptTo = []
        #: SMTP mode ('SMTP' (default) or 'ESMTP' when STARTTLS or AUTH was used)
        self.smtpMode = 'SMTP'
        #: Authenticator currently in use
        self.authenticator = None
        #: Username
        self.username = None
        #: Body buffer
        self.buffer = bytearray('')
        #: List of headers from mail
        self.headers = []
        #: Job ID (DB row ID)
        self.jobId = None
        # Initialize TLS
        tls = self.server.config('tls', {})
        tls.update(self.config('tls', {}))
        if tls.get('enabled', False):
            if softAssert(
                (tls.get('key'), tls.get('certificate')).count(None) == 0,
                _('TLS key and certificate must both be present')
            ):
                #: TLS enabled
                self.tlsEnabled = True
                #: TLS key file
                self.tlsKey = tls['key']
                #: TLS certificate file
                self.tlsCertificate = tls['certificate']
                #: STARTTLS mode (True: use STARTTLS, False: start connection in TLS)
                self.tlsStart = not not tls.get('starttls')
                self.log.info('TLS is ON')
        # Initialize authorizers
        if self.server.config.has('authorisation'):
            self.authorizer = dict(
                [(key, auth(self, self.server.config.authorisation._[key])) for key, auth in self.authorizers.items()]
            )

    def reset(self):
        '''
        Reset transaction

        Clears all data regarding the mail transfer session
        '''
        self.mailFrom = None
        self.rcptTo = []
        self.headers = []
        self.buffer = bytearray('')
        self.job.rollback()

    def start(self): # pylint: disable=E0202
        '''
        Handle a complete SMTP connection from connect to disconnect
        '''
        self.socket, self.address = self.listener.accept()
        if not self.tlsStart:
            self.socket = eventlet.green.ssl.wrap_socket(self.socket, self.tlsKey, self.tlsCertificate, True)
        self.sockfile = self.socket.makefile() # pylint is confused: pylint: disable=E1103
        self.messageId = uuid.uuid4().hex
        self.log.info('%s:Connection from %s', self.messageId, self.address)
        self.advertisedAddress = self.config('address', self.server.config('address', self.address[0]))
        self.state = self.commandState
        self.send(220, self.advertisedAddress, self.description)
        # Read from socket. Handlers like handleQuit() can set ``self.state`` to None to stop
        while self.state:
            line = self.inputLine()
            if not line:
                # Connection closed by client
                break
            self.state(line.rstrip())
        try:
            self.socket.shutdown(2)
        except ClientException: # pylint: disable=W0703
            self.log.exception('%s:Closing connection', self.messageId)
        self.log.info('%s:Connection %s closed', self.messageId, self.address)
        self.messageId = None

    def commandState(self, line):
        '''
        Handle line in command state

        :param string line: input line

        In command state, lines are interpreted as SMTP commands. The line is split into words separated by white space. If a
        method named ``handle<command>`` (where command is the title case form of the input command) exists, it is called with
        the list of words. If none exists, a 500 error is sent back.
        '''
        if not line:
            return
        self.log.debug('%s:<==%s', self.messageId, line.rstrip())
        words = line.split()
        method = getattr(self, 'handle' + words[0].title(), None)
        if method:
            method(words)
        else:
            self.send(500)

    def headerState(self, line):
        '''
        Handle line in HEADER state

        :param string line: input line

        In HEADER state, lines are interpreted as mail headers upto a empty line. An empty line will switch to the DATA state.
        This will also write a cause a record to be written into the Job table.
        '''
        if line:
            self.job.addHeader(line)
        else:
            # Insert :mailheader:`Message-ID` header if necessary
            if not any(k for k in self.headers if k.lower().startswith('message-id:')):
                self.job.insertHeader('Message-ID: <%s@%s>' % (self.messageId, self.advertisedAddress))
            # Insert :mailheader:`Received` header
            try:
                clientIp = socket.gethostbyname(self.client)
            except socket.gaierror:
                clientIp = 'unknown'
            received = self.wrapper.wrap(
                'Received: from %s [%s, real %s] by %s with %s id %s; %s' % (
                    self.client,
                    clientIp,
                    self.address[0],
                    self.advertisedAddress,
                    self.smtpMode,
                    self.messageId,
                    email.Utils.formatdate(localtime=True)
                )
            )
            self.job.insertHeader('\r\n'.join(received))
            self.state = self.dataState

    def dataState(self, line):
        '''
        Handle line in DATA state

        :param string line: input line

        In DATA state, all lines are interpreted as data upto a single line consisting of a period character which will switch
        to COMMAND state.
        '''
        if line == '.':
            self.job.commit()
            self.reset()
            self.state = self.commandState
            self.sendOk()
            return
        if line and line[0] == '.':
            line = line[1:]
        self.job.addBody(line + '\r\n')

    def authenticationState(self, line):
        '''
        Handle line in authentication state

        :param line:
        '''
        self.log.debug('%s:<==%s', self.messageId, line.rstrip())
        assert self.authenticator, 'INTERNAL ERROR: In authentication state but no authenticator in use'
        end = self.authenticator.handleLine(line)
        if end:
            self.state = self.commandState

    def authenticate(self, username, password):
        '''
        Set authentication credentials

        :param username:
        :param password:
        :return status code:

        Searches all authorizers for one that authenticates against the given username/password. If one is found, 235 is
        returned or 535 if not.
        '''
        self.username = username
        return self.send(235 if any(a.authorize(username, password) for a in self.authorizer.itervalues()) else 535)

    def inputLine(self):
        '''
        Read line from socket

        :return: line from socket
        '''
        return self.sockfile.readline() #pylint: disable=E1103

    def send(self, code, *args, **kwargs):
        '''
        Send line to socket

        :param int code: status code
        :param strings \\*args: zero or more strings to fill %-formats
        :param \\*\\*msg: list, tuple, or single object to send instead of message associated with code

        If keyword argument ``msg`` is present, it constitutes the whole message and Arguments in ``*args`` are ignored in this
        case. If ``msg`` is a tuple or list, the elements are sent according to the rule of RFC 1869. If ``msg`` is not present,
        a text associated with the code is sent with its format codes filled in from the arguments in ``*args``.
        '''
        assert type(code) is int
        message = kwargs.get('msg')
        if message:
            if type(message) not in (list, tuple):
                message = (str(message),)
        else:
            message = [self.messages[code] % args]
        for i in range(len(message)):
            m = message[i]
            if type(m) is not str:
                m = str(m)
            s = '%d%s%s\r\n' % (code, '-' if i + 1 < len(message) else ' ', m)
            self.log.debug('%s:==>%s', self.messageId, s[:-2])
            self.socket.send(s)

    def sendOk(self, msg='OK'):
        '''
        Send a 250 OK message

        :param string msg: optional message. Default is "OK"
        '''
        self.send(250, msg)

    def handleHelo(self, words):
        '''
        Handle HELO <domain>

        :param string-list words: command and arguments
        '''
        if len(words) != 2:
            self.send(501)
            return
        self.client = words[1]
        self.send(250, msg=('Hello %s! Nice to meet you.' % self.client, 'STARTTLS', 'AUTH PLAIN'))

    handleEhlo = handleHelo

    def handleMail(self, words):
        '''
        Handle MAIL FROM:<source> or MAIL FROM <source>

        :param string-list words: command and arguments
        '''
        if len(words) == 2:
            # Check for MAIL FROM:<source>
            if words[1][:5].upper() != 'FROM:':
                self.send(501)
                return
            mailFrom = words[1][5:]
        elif len(words) == 3:
            # Check for MAIL FROM <source>
            if words[1].upper() not in ('FROM', 'FROM:'):
                self.send(501)
                return
            mailFrom = words[2]
            if not mailFrom:
                self.send(501)
        else:
            self.send(501)
            return
        mailFrom = self.mailAddressRe.match(mailFrom)
        if not mailFrom:
            self.send(501)
            return
        # If a path is supplied, take only the last element
        mailFrom = mailFrom.group(1).split(':')[-1]
        if not self.client:
            self.send(503)
            return
        self.mailFrom = mailFrom
        self.sendOk()

    def handleRcpt(self, words):
        '''
        Handle RCPT TO:<destination> or RCPT TO <destination>

        :param string-list words: command and arguments
        '''
        if len(words) == 2:
            # Check for RCPT TO:<destination>
            if words[1][:3].upper() != 'TO:':
                self.send(501)
                return
            rcptTo = words[1][3:]
        elif len(words) == 3:
            # Check for RCPT TO <destination>
            if words[1].upper() not in ('TO', 'TO:'):
                self.send(501)
                return
            rcptTo = words[2]
        else:
            self.send(501)
            return
        rcptTo = self.mailAddressRe.match(rcptTo)
        if not rcptTo:
            self.send(501)
            return
        # If a path is supplied, take only the last element
        rcptTo = rcptTo.group(1).split(':')[-1]
        if not self.client:
            self.send(503)
            return
        self.rcptTo.append(rcptTo)
        self.sendOk()

    def handleData(self, words):
        '''
        Handle DATA

        :param string-list words: command and arguments

        A Job row is written to the database
        '''
        if len(words) != 1:
            self.send(501)
            return
        if not self.client:
            self.send(503)
            return
        if not self.mailFrom or not self.rcptTo:
            self.send(503)
            return
        self.send(354)
        self.job = spooler.Job(self.server.spooler.spoolFile, self.mailFrom, self.messageId)
        for r in self.rcptTo:
            self.job.addDestination(r)
        self.state = self.headerState

    def handleQuit(self, words):
        '''
        Handle QUIT command

        :param string-list words: command and arguments
        '''
        if len(words) != 1:
            self.send(501)
        self.send(221, self.advertisedAddress)
        self.state = None

    def handleNoop(self, _words):
        '''
        Handle NOOP command

        :param string _words: unused
        '''

    def handleHelp(self, _words):
        '''
        Handle HELP command

        :param string _words: unused
        '''
        self.send(214)

    def handleRset(self, _words):
        '''
        Handle RSET command

        :param string _words: unused
        '''
        self.reset()

    def handleStarttls(self, words):
        '''
        Handle STARTTLS command

        :param string words:
        '''
        if len(words) != 1:
            self.send(501)
        if self.tlsEnabled and self.tlsStart:
            self.send(220, msg='Go ahead')
            self.socket = eventlet.green.ssl.wrap_socket(
                self.socket, certfile=self.tlsCertificate, keyfile=self.tlsKey, server_side=True
            )
            self.sockfile = self.socket.makefile()
        else:
            self.send(500)

    def handleAuth(self, words):
        '''
        Handle AUTH command
        '''
        auth = words[1].upper()
        if auth in self.authenticators:
            self.authenticator = self.authenticators[auth](self)
            if not self.authenticator.start(words):
                self.state = self.authenticationState
        else:
            self.send(504)