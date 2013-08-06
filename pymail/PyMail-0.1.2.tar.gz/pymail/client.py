'''
SMTP client
'''

from .debug import D
from eventlet import timeout
from eventlet.green import socket
import base64
import eventlet
import logging
import re
import sys

CONNECT_TIMEOUT = 10

COMMAND_MODE = 1
DATA_MODE = 2

class ClientException(RuntimeError):
    '''
    Execption raised when response from SMTP server is not the expected one
    '''
    pass

class TemporaryError(RuntimeError):
    '''
    Execption raised when a temporary error prevented a connection
    '''
    pass

class Session(object):
    '''
    SMTP session
    '''

    #: Regex to parse an SMTP server response
    serverResponseRe = re.compile(r'(\d{3})([ -])(.*)')

    def __init__(self, config, mailHosts, clientAddress, messageId, source, destination):
        '''
        Create Client object

        :param config:
        :param string mailHosts:
        :param string clientAddress: if not supplied, `socket.gethostname()` is taken
        :param string messageId:
        :param string source:
        :param string destination:
        '''
        #: Destination's config section
        self.config = config
        #: Address of server to contact
        self.mailHosts = mailHosts
        #: Connection host (effective)
        self.host = None
        #: Connection port
        self.port = None
        #: Client address to use in protocol
        self.clientAddress = clientAddress
        #: Message ID
        self.messageId = messageId
        #: Source e-mail address
        self.source = source
        #: Destination e-mail address
        self.destination = destination
        #: Protocol status
        self.status = COMMAND_MODE
        #: Socket (set in one of the open...() methods)
        self.socket = None
        #: Socket file (set in one of the open...() methods)
        self.sockfile = None
        #: DATA bytes sent
        self.dataSize = 0
        #: Logger
        self.log = logging.getLogger('pymail.client.Client')
        status = 0
        # Since we are an MTA we try port 25 before 587. It isn't even strictly correct to use 587 as an MTA
        for m, p in (self.starttls, 25), (self.tls, 465), (self.starttls, 587), (self.plain, 25), (self.plain, 587):
            try:
                self.log.debug('Try %s on port %d', m, p)
                m(p)
            except TemporaryError:
                status += 1
            except:
                pass
            else:
                self.sendLine('MAIL FROM:<%s>' % self.source)
                response = self.read()
                if response[0][0] != '250':
                    raise ClientException(collected(response))
                self.sendLine('RCPT TO:<%s>' % self.destination)
                response = self.read()
                if response[0][0] != '250':
                    raise ClientException(collected(response))
                self.log.debug('connected to %s:%d', self.host, self.port)
                return
        if status:
            raise TemporaryError('Temporary error connecting to %s' % '/'.join(self.mailHosts))
        else:
            raise ClientException('Could not establish connection with %s' % '/'.join(self.mailHosts))

    def close(self):
        '''
        Close connection

        :raise ClientException: on improper response from QUIT command

        Signs off with the SMTP server
        '''
        self.sendLine('QUIT')
        response = self.read()
        if response[0][0] != '221':
            raise ClientException(collected(response))

    def read(self):
        '''
        Read server response

        :return: list of tuples (code, text)
        :raise ClientException: on unparsable response from server

        Reads a server response, possibly with dash continuations and returns all in a list
        '''
        response = []
        while True:
            line = self.sockfile.readline()
            if not line:
                break
            line = line[:-2]
            parsed = self.serverResponseRe.match(line)
            if not parsed:
                raise ClientException('Invalid response from server: ' + line)
            self.log.debug('<==%s', repr(line))
            response.append((parsed.group(1), parsed.group(3)))
            if parsed.group(2) != '-':
                break
        return response

    def sendLine(self, msg):
        '''
        Send line

        :param string msg:

        Sends a line and terminates it by CR/LF.
        '''
        self.socket.sendall(msg + '\r\n')
        for line in msg.split('\r\n'):
            self.log.debug('-->%s', line)

    def startData(self):
        '''
        Send a DATA command and switch to DATA_MODE
        '''
        self.sendLine('DATA')
        response = self.read()
        if response[0][0] != '354':
            raise ClientException('Expected 354 response from DATA command, got "%s"' % response)
        self.status = DATA_MODE
        self.dataSize = 0

    def sendData(self, data):
        '''
        Send body

        :param string data:

        Send data as-is
        '''
        assert self.status == DATA_MODE, 'Not in DATA_MODE'
        self.socket.sendall(data)
        self.dataSize += len(data)

    def endData(self):
        '''
        Send terminating . line and switchg to COMMAND_MODE
        '''
        self.sendLine('.')
        response = self.read()
        if response[0][0] != '250':
            raise ClientException('Expected 250 response from end of data, got "%s"' % response)
        self.status = COMMAND_MODE
        self.log.info('Message %s: sent %d DATA bytes', self.messageId, self.dataSize)

    def open(self):
        '''
        '''
        tempError = 0
        for m in self.mailHosts:
            try:
                with timeout.Timeout(CONNECT_TIMEOUT):
                    self.socket.connect((m, self.port))
            except:
                self.log.debug('Connect to %s:%d yielded %s', m, self.port, sys.exc_info()[1])
            else:
                self.sockfile = self.socket.makefile()
                self.host = m
                break
        else:
            # At the moment we treat all connection errors as temporary. This could turn out to be false however
            raise TemporaryError('Could not make a connection to port %d at any of %s' % self.port, ', '.join(self.mailHosts))

    def starttls(self, port):
        '''
        Open connection and negotiate an SMTP session until after optional PLAIN authentication

        :raise ClientException:
        :raise TemporaryError:

        Opens a connection, sends EHLO and receives server response, which must include a STARTTLS message. If the server
        supports PLAIN authentication and username and password are provided in configuration, an authentication is done.
        '''
        self.port = port
        self.socket = socket.socket()
        self.open()
        self.log.debug('Connected with STARTTLS to %s:%d', self.host, self.port)
        response = self.read()
        if len(response) != 1 or response[0][0] != '220':
            raise TemporaryError(collected(response))
        self.sendLine('EHLO %s' % self.clientAddress)
        response = self.read()
        if 'STARTTLS' not in (r[1].upper() for r in response):
            raise ClientException('Server does not support STARTTLS')
        self.sendLine('STARTTLS')
        response = self.read()
        if response[0][0] != '220':
            raise ClientException(collected(response))
        self.socket = eventlet.wrap_ssl(self.socket)
        self.sockfile = self.socket.makefile()
        self.sendLine('EHLO %s' % self.clientAddress)
        response = self.read()
        if response[0][0] != '250':
            raise TemporaryError(collected(response))
        authentication = (r for r in (r[1].upper() for r in response) if 'AUTH' in r and 'PLAIN' in r)
        username = self.config('username', None)
        password = self.config('password', None)
        if authentication and username and password:
            self.sendLine('AUTH PLAIN %s' % base64.encodestring('\0%s\0%s' % (username, password)))
            response = self.read()
            if response[0][0] != '235':
                raise ClientException(collected(response))

    def tls(self, port):
        '''
        Open connection and negotiate an SMTP session until after optional PLAIN authentication

        :raise ClientException:
        :raise TemporaryError:

        Opens a connection in SSL, sends EHLO and receives server response. If the server supports PLAIN authentication and
        username and password are provided in configuration, an authentication is done.
        '''
        self.port = port
        self.socket = eventlet.wrap_ssl(socket.socket())
        self.open()
        self.log.debug('Connected with TLS to %s:%d', self.host, self.port)
        response = self.read()
        if len(response) != 1 or response[0][0] != '220':
            raise ClientException(collected(response))
        self.sendLine('EHLO %s' % self.clientAddress)
        response = self.read()
        authentication = [r for r in [r[1].upper() for r in response] if 'AUTH' in r and 'PLAIN' in r]
        username = self.config('username', None)
        password = self.config('password', None)
        if authentication and username and password:
            self.sendLine('AUTH PLAIN %s' % base64.encodestring('\0%s\0%s' % (username, password)))
            response = self.read()
            if response[0][0] != '235':
                raise ClientException(collected(response))

    def plain(self, port):
        '''
        Open connection to port 25, negotiate an SMTP session *without* authentication

        :raise ClientException:
        :raise TemporaryError:

        Opens a connection, sends EHLO and receives server response. No AUTH authentication is attempted since the connection
        is not encrypted. If the server insists on an authentication, this connection will fail.
        '''
        self.port = port
        self.socket = socket.socket()
        self.open()
        self.log.debug('Connected plain to %s:%d', self.host, self.port)
        response = self.read()
        if len(response) != 1 or response[0][0] != '220':
            raise TemporaryError(collected(response))
        self.sendLine('EHLO %s' % self.clientAddress)
        response = self.read()
        if response[0][0] != '250':
            raise TemporaryError(collected(response))

def collected(items):
    return ('\r\n'.join(i[1] for i in items))
