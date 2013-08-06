'''
This module contains classes that deliver a mail message to some destination (ie. to the Internet by SMTP or to a local MailDir
mailbox)
'''

#from .debug import D
from . import client, error
import dns.resolver
import logging
import eventlet

class Sink(object):
    '''
    Base class for mail sinks

    Synopsis::

        sink = SomeSink(sconfig, config, messageId, source, destination, headers)
        sink.open()
        for block in blocks:
            sink.sendBodyBlock(block)
        sink.close()
    '''

    def __init__(self, sconfig, config, messageId, source, destination, headers):
        '''
        Create Sink object

        :param sconfig: Server configuration
        :param config: Local configuration
        :param messageId:
        :param string source:
        :param string destination:
        :param list headers:

        To be called by deriving classes' `__init__` method.
        '''
        #: Server configuration
        self.sconfig = sconfig
        #: Local configuration
        self.config = config
        #: Logger
        self.log = logging.getLogger('pymail.sink.Smtp')
        #: Message-ID
        self.messageId = messageId
        #: Source address
        self.source = source
        #: Destination address
        self.destination = destination
        #: List of headers
        self.headers = headers
        #: E-Mail domain part
        self.domain = self.destination.partition('@')[2]
        #: Client session
        self.clientSession = None

    def open(self):
        '''
        Open sink

        Readies the sink to receive the mail body.

        To be overridden by subclass
        '''
        raise NotImplementedError('open')

    def close(self):
        '''
        Close sink

        To be overridden by subclass
        '''
        raise NotImplementedError('close')

    def sendBodyBlock(self, block):
        '''
        Send body block

        :param string block:

        To be overridden by subclass
        '''
        raise NotImplementedError('sendBodyBlock')

class Smtp(Sink):
    '''
    Mail delivery to a SMTP server
    '''

    def __init__(self, sconfig, config, messageId, source, destination, headers):
        if '@' not in destination:
            raise error.MailError('Message %s: address must have a @domain part: %s' % (messageId, destination))
        super(Smtp, self).__init__(sconfig, config, messageId, source, destination, headers)
        #: Client session
        self.clientSession = None

    def open(self):
        '''
        Open connection to mail host

        :raise error.MailError:
        '''
        self.log.info('Send %s to %s via SMTP', self.messageId, self.destination)
        self.clientSession = client.Session(
            self.config,
            self._mailersFor(self.domain),
            self.sconfig('address', eventlet.greenio.socket.gethostname()),
            self.messageId,
            self.source,
            self.destination
        )
        self.clientSession.startData()
        for h in self.headers:
            self.clientSession.sendLine(h)
        self.clientSession.sendLine('') # Terminate header section

    def close(self):
        self.clientSession.endData()
        self.clientSession.close()

    def sendBodyBlock(self, block):
        self.clientSession.sendData(block)

    def _mailersFor(self, domain):
        '''
        Get a list of preferred mailers for domain, in order of preference

        :param string domain:
        :return: list of domains
        '''
        try:
            records = dns.resolver.query(domain, 'MX')
        except: # pylint: disable=bare-except
            return [domain]
        return [
            rec[0] for rec in
                sorted([(rec.exchange.to_text(), rec.preference) for rec in records], lambda a, b: cmp(a[1], b[1]))
        ] + [domain]

class MailDir(Sink):
    '''
    MailDir mailboxes
    '''
