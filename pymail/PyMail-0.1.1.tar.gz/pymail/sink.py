'''
This module contains classes that deliver a mail message to some destination (ie. to the Internet by SMTP or to a local MailDir
mailbox)
'''

import greenfile
import error
import mailbox
import client
import dns.resolver
from debug import D
import os
from test.test_socket import try_address
import trace

class Sink(object):
    '''
    Base class for mail sinks
    
    Derived classes overwrite the `send` method
    '''

    def __init__(self, config):
        '''
        Create Sink object

        :param config: Local configuration
        
        To be called by deriving classes' `__init__` method.
        '''
        #: Local configuration
        self.config = config

    def send(self, mailFrom, rcptTo, dataFilename):
        '''
        Send message
        
        :param string mailFrom:
        :param string rcptTo:
        :param string dataFilename:
        
        To be overwritten by deriving classes
        '''

class Smtp(Sink):
    '''
    Mail delivery to a SMTP server
    '''

    def __init__(self, config):
        super(Smtp, self).__init__(config)

    def send(self, mailFrom, rcptTo, dataFilename):
        D('SEND ', dataFilename, ' to ', rcptTo)
        try:
            user, domain = rcptTo.split('@')
        except ValueError:
            raise error.MailError('Mail address must have a @domain part')
        mailers = self.mailer(domain)
        # Try all mailers to send message until sending to one succeeds
        for mailer in mailers:
            mailFile = file(dataFilename)
            if self.send2(mailer, mailFrom, rcptTo, mailFile): # TODO: supply username, password, unsecure from config
                break
            
    def send2(self, mailer, mailFrom, rcptTo, mailFile):
        '''
        Send mail file to definitive mail host
        '''
        cl = client.Client(mailer)
        return cl.send(mailFrom, rcptTo, mailFile)

    def mailer(self, domain):
        '''
        Get a list of preferred mailers for domain, in order of preference
        
        :param string domain:
        :return: list of domains
        '''
        try:
            records = dns.resolver.query(domain, 'MX')
        except:
            return [domain]
        return [
            rec[0] for rec in
                sorted([(rec.exchange.to_text(), rec.preference) for rec in records], lambda a, b: cmp(a[1], b[1]))
        ]

class MailDir(Sink):
    '''
    MailDir mailboxes
    '''

    def __init__(self, config):
        super(MailDir, self).__init__(config)

    def send(self, mailFrom, rcptTo, dataFilename):
        at = rcptTo.find('@')
        if at >= 0:
            user = rcptTo[:at]
        else:
            user = rcptTo
        boxDir = self.config.directory.format(user=user)
        D('MailDir ', boxDir)
        try:
            for d in ('new', 'tmp', 'cur'):
                os.makedirs(os.path.join(boxDir, d), 0777)
        except OSError:
            pass
        box = mailbox.Maildir(boxDir, None, True)
        box.add(greenfile.File(dataFilename))
        D('DELIVERED MESSAGE ', dataFilename, ' TO MAILDIR ', rcptTo)
