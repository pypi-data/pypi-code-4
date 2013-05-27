'''
SMTP client
'''

from debug import D
from eventlet.green import socket
import eventlet
import re
import base64

class Client(object):
    '''
    SMTP client
    '''
    
    serverResponseRe = re.compile('(\d{3})([ -])(.*)')
    
    def __init__(self, mailHost, clientAddress=None):
        '''
        Create Client object
        
        :param string mailHost:
        :param string clientAddress: if not supplied, `socket.gethostname()` is taken
        '''
        #: Mail host address
        self.mailHost = mailHost
        #: Client address
        self.clientAddress = clientAddress or socket.gethostname()
        #: Socket
        self.socket = None
        #: Socket file
        self.sockfile = None
        
    def read(self):
        '''
        Read server response
        
        :return: list of tuples (code, text)
        
        Reads a server response, possibly with dash continuations and returns all in a list
        '''
        input = []
        while True:
            line = self.sockfile.readline()
            if not line:
                break
            line = line[:-2]
            parsed = self.serverResponseRe.match(line)
            if not parsed:
                raise RuntimeError('Invalid input from server: ' + line)
            D('<==', repr(line))
            input.append((parsed.group(1), parsed.group(3)))
            if parsed.group(2) != '-':
                break
        return input
            
    def open25tls(self, username, password):
        '''
        Open connection to port 25, negotiate an SMTP session until after PLAIN authentication
        
        :param username:
        :type username: string or None
        :param password:
        :type password: string or None
        :return: True, if all goes well
        
        Opens a connection, sends EHLO and receives server response, which must include a STARTTLS message. If the server
        supports PLAIN authentication and username and password are provided (not None) an authentication is done.
        '''
        try:
            self.socket = socket.socket()
            self.socket.connect((self.mailHost, 25))
            self.sockfile = self.socket.makefile()
            input = self.read()
            D(input)
            if len(input) != 1 or input[0][0] != '220':
                return False
            self.snd('EHLO %s' % self.clientAddress)
            input = self.read()
            if 'STARTTLS' not in [r[1].upper() for r in input]:
                return False
            self.snd('STARTTLS')
            input = self.read()
            if input[0][0] != '220':
                return False
            self.socket = eventlet.wrap_ssl(self.socket)
            self.sockfile = self.socket.makefile()
            self.snd('EHLO %s' % self.clientAddress)
            input = self.read()
            if input[0][0] != '250':
                return False
            authentication = [r for r in [r[1].upper() for r in input] if 'AUTH' in r and 'PLAIN' in r]
            if authentication and username and password:
                self.snd('AUTH PLAIN %s' % base64.encodestring('\0%s\0%s' % (username, password)))
                input = self.read()
                if input[0][0] != '235':
                    D('Expected 235 response')
                    return False
            return True
        except:
            import sys
            D(sys.exc_info())
            return False

    def open465(self, username, password):
        '''
        Open connection to port 465, negotiate an SMTP session until after PLAIN authentication
        
        :param string or None username:
        :param string or None password:
        :return: socket, if server supports STARTTLS, or None
        
        Opens a connection in SSL, sends EHLO and receives server response. If the server supports PLAIN authentication and 
        username and password are provided (not None) an authentication is done.
        '''
        try:
            self.socket = eventlet.wrap_ssl(socket.socket())
            self.socket.connect((self.mailHost, 465))
            self.sockfile = self.socket.makefile()
            input = self.read()
            D(input)
            if len(input) != 1 or input[0][0] != '220':
                return False
            self.snd('EHLO %s' % self.clientAddress)
            input = self.read()
            authentication = [r for r in [r[1].upper() for r in input] if 'AUTH' in r and 'PLAIN' in r]
            if authentication and username and password:
                self.snd('AUTH PLAIN %s' % base64.encodestring('\0%s\0%s' % (username, password)))
                input = self.read()
                if input[0][0] != '235':
                    D('Expected 235 response')
                    return False
            return True
        except:
            import sys
            D(sys.exc_info())
            return None
    
    def open25(self):
        # TODO: implement
        return False

    def snd(self, msg):
        self.socket.send(msg + '\r\n')
        D('->', msg)
                
    def send(self, mailFrom, rcptTo, mailFile, username=None, password=None, unsecure=False):
        '''
        Send mail file in a dialog with SMTP server 
        
        :param string mailFrom:
        :param string rcptTo:
        :param file mailFile:
        :param string username: username for SMTP authentication
        :param string password: password for SMTP authentication
        :param bool unsecure: whether unsecure communication is allowed
        :return: True if message was sent successfully
        
        Sends a message file to mail host. First, port 25 is tried, but only with STARTTLS support. If STARTTLS is not
        supported, port 465 with SSL is tried, if this is not supported, then, as a last resort, port 25 without STARTTLS is
        used, *if* `unsecure` is `True`.
        '''
        if self.open25tls(username, password) or self.open465(username, password) or not unsecure and self.open25():
            self.snd('MAIL FROM:<%s>' % mailFrom)
            input = self.read()
            if input[0][0] != '250':
                D('Expected 250 response')
                return False
            self.snd('RCPT TO:<%s>' % rcptTo)
            input = self.read()
            if input[0][0] != '250':
                D('Expected 250 response')
                return False
            self.snd('DATA')
            input = self.read()
            if input[0][0] != '354':
                D('Expected 354 response')
                return False
            for line in mailFile:
                line = line.rstrip()
                if line and line[0] == '.':
                    line = '.' + line
                self.snd(line)
            self.snd('.')
            input = self.read()
            if input[0][0] != '250':
                D('Expected 250 response')
                return False
            self.snd('QUIT')
            input = self.read()
            if input[0][0] != '221':
                D('Expected 221 response - ignoring')
            return True
        else:
            D('NO CONNECTION')
            return False