""" :mod:`hedwig.message`
    ~~~~~~~~~~~~~~~~~~~~~

"""
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from os import getpid
from random import randrange
from socket import getfqdn
from sys import getdefaultencoding
from time import gmtime, strftime, time


SUPPORTED_CONTENT_SUBTYPES = frozenset(['plain', 'html'])


def make_message_id(idstring=None):
    timeval = time()
    utcdate = strftime('%Y%m%d%H%M%S', gmtime(timeval))
    pid = getpid()
    randint = randrange(100000)
    if idstring is None:
        idstring = ''
    else:
        idstring = '.' + idstring
    DNS_NAME = getfqdn()
    msgid = '<{0}.{1}.{2}{3}@{4}>'.format(utcdate, pid, randint, idstring,
                                          DNS_NAME)


class EmailMessage(object):
    """
    Email.
    """

    def __init__(self, subject='', body='', from_=None, to=None, bcc=None,
                 attachments=(), headers={}, encoding=None,
                 content_subtype='html'):
        if from_ and not isinstance(from_, basestring):
            raise TypeError('from_ must be a string, not ' + repr(from_))
        if to:
            if not isinstance(to, (list, tuple)):
                to = [to]
            for each in to:
                if not isinstance(each, basestring):
                    raise TypeError('to must be a list or tuple contains '
                                    'basestring')
        self.to = to or []
        if bcc:
            if not isinstance(bcc, (list, tuple)):
                bcc = [bcc]
            for each in bcc:
                if not isinstance(each, basestring):
                    raise TypeError('bcc must be a list or tuple contains '
                                    'basestring')
        self.bcc = bcc or []
        self.from_ = from_
        self.subject = subject
        if encoding is None and isinstance(body, unicode):
            body = body.encode('utf-8')
            encoding = 'utf-8'
        self.body = body
        self.attachments = []
        for file_ in attachments:
            raise NotImplementedError()
        self.extra_headers = dict(headers)
        self.encoding = encoding or getdefaultencoding()
        if content_subtype not in SUPPORTED_CONTENT_SUBTYPES:
            supports = SUPPORTED_CONTENT_SUBTYPES
            if len(supports) == 1:
                supports = supports[0]
            else:
                supports = ', '.join(supports[:-1]) + ' or %s' % supports[-1]
            raise ValueError('content_subtype must be %s' % supports)
        self.content_subtype = content_subtype

    def message(self):
        """ A message of the email. """
        body = self.body
        if not isinstance(body, str):
            body = unicode(body) if hasattr(body, '__unicode__') else str(body)
        if isinstance(body, unicode):
            body = body.encode(self.encoding)
        msg = MIMEText(body, self.content_subtype, self.encoding)
        msg = self._create_message(msg)
        msg['Subject'] = self.subject
        msg['From'] = self.extra_headers.get('From', self.from_)
        msg['To'] = ', '.join(self.to)
        header_names = [key.lower() for key in self.extra_headers]
        if 'date' not in header_names:
            msg['Date'] = formatdate()
        if 'message-id' not in header_names:
            msg['Message-ID'] = make_message_id()
        for name, value in self.extra_headers.items():
            if name.lower() == 'from':
                continue
            msg[name] = value
        return msg

    def _create_message(self, message):
        if self.attachments:
            raise NotImplementedError()
        return message

    @property
    def recipients(self):
        """ A list of all recipients of the email. """
        return self.to + self.bcc

    def attach(self, *args):
        raise NotImplementedError()

    def __repr__(self):
        cls = type(self)
        mod = cls.__module__
        mod = '' if __name__ == mod else mod + '.'
        args = [
            ('subject', self.subject),
            ('body', self.body),
            ('from_', self.from_),
            ('to', self.to),
            ('bcc', self.bcc),
            ('attachments', self.attachments),
            ('headers', self.extra_headers),
            ('encoding', self.encoding),
        ]
        kwargs = ', '.join('{0}={1!r}'.format(k, v) for k, v in args)
        return '{0}{1}({2})'.format(mod, cls.__name__, kwargs)
