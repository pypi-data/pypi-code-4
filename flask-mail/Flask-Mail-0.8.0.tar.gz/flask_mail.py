# -*- coding: utf-8 -*-
"""
    flaskext.mail
    ~~~~~~~~~~~~~

    Flask extension for sending email.

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import with_statement

__version__ = '0.8.0'

import blinker
import smtplib
import time

from email import charset
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate, formataddr, make_msgid, parseaddr
from contextlib import contextmanager

from flask import current_app

charset.add_charset('utf-8', charset.SHORTEST, None, 'utf-8')


class FlaskMailUnicodeDecodeError(UnicodeDecodeError):
    def __init__(self, obj, *args):
        self.obj = obj
        UnicodeDecodeError.__init__(self, *args)

    def __str__(self):
        original = UnicodeDecodeError.__str__(self)
        return '%s. You passed in %r (%s)' % (original, self.obj, type(self.obj))


def force_text(s, encoding='utf-8', errors='stricts'):
    if isinstance(s, unicode):
        return s
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = s.__unicode__()
            else:
                s = unicode(bytes(s), encoding, errors)
        else:
            s = s.decode(encoding, errors)
    except UnicodeDecodeError, e:
        if not isinstance(s, Exception):
            raise FlaskMailUnicodeDecodeError(s, *e.args)
        else:
            s = ' '.join([force_text(arg, encoding, errors) for arg in s])
    return s


def sanitize_address(addr, encoding='utf-8'):
    if isinstance(addr, basestring):
        addr = parseaddr(force_text(addr))
    nm, addr = addr

    # This try-except clause is needed on Python 3 < 3.2.4
    # http://bugs.python.org/issue14291
    try:
        nm = Header(nm, encoding).encode()
    except UnicodeEncodeError:
        nm = Header(nm, 'utf-8').encode()

    try:
        addr.encode('ascii')
    except UnicodeEncodeError:  # IDN
        if '@' in addr:
            localpart, domain = addr.split('@', 1)
            localpart = str(Header(localpart, encoding))
            domain = domain.encode('idna').decode('ascii')
            addr = '@'.join([localpart, domain])
        else:
            addr = Header(addr, encoding).encode()
    return formataddr((nm, addr))


def sanitize_addresses(addresses):
    return map(lambda e: sanitize_address(e), addresses)


class Connection(object):
    """Handles connection to host."""

    def __init__(self, mail):
        self.mail = mail

    def __enter__(self):
        if self.mail.suppress:
            self.host = None
        else:
            self.host = self.configure_host()

        self.num_emails = 0

        return self

    def __exit__(self, exc_type, exc_value, tb):
        if self.host:
            self.host.quit()

    def configure_host(self):
        if self.mail.use_ssl:
            host = smtplib.SMTP_SSL(self.mail.server, self.mail.port)
        else:
            host = smtplib.SMTP(self.mail.server, self.mail.port)

        host.set_debuglevel(int(self.mail.debug))

        if self.mail.use_tls:
            host.starttls()
        if self.mail.username and self.mail.password:
            host.login(self.mail.username, self.mail.password)

        return host

    def send(self, message):
        """Sends message.

        :param message: Message instance.
        """

        if message.date is None:
            message.date = time.time()

        if self.host:
            self.host.sendmail(message.sender,
                               message.send_to,
                               message.as_string())

        email_dispatched.send(message, app=current_app._get_current_object())

        self.num_emails += 1

        if self.num_emails == self.mail.max_emails:
            self.num_emails = 0
            if self.host:
                self.host.quit()
                self.host = self.configure_host()

    def send_message(self, *args, **kwargs):
        """Shortcut for send(msg).

        Takes same arguments as Message constructor.

        :versionadded: 0.3.5
        """

        self.send(Message(*args, **kwargs))


class BadHeaderError(Exception):
    pass


class Attachment(object):
    """Encapsulates file attachment information.

    :versionadded: 0.3.5

    :param filename: filename of attachment
    :param content_type: file mimetype
    :param data: the raw file data
    :param disposition: content-disposition (if any)
    """

    def __init__(self, filename=None, content_type=None, data=None,
                 disposition=None, headers=None):
        self.filename = filename
        self.content_type = content_type
        self.data = data
        self.disposition = disposition or 'attachment'
        self.headers = headers or {}


class Message(object):
    """Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address, or **MAIL_DEFAULT_SENDER** by default
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances
    :param reply_to: reply-to address
    :param date: send date
    :param charset: message character set
    :param extra_headers: A dictionary of additional headers for the message
    """

    def __init__(self, subject,
                 recipients=None,
                 body=None,
                 html=None,
                 sender=None,
                 cc=None,
                 bcc=None,
                 attachments=None,
                 reply_to=None,
                 date=None,
                 charset=None,
                 extra_headers=None):

        sender = sender

        if isinstance(sender, tuple):
            sender = "%s <%s>" % sender

        self.recipients = recipients or []
        self.subject = subject
        self.sender = sender
        self.reply_to = reply_to
        self.cc = cc or []
        self.bcc = bcc or []
        self.body = body
        self.html = html
        self.date = date
        self.msgId = make_msgid()
        self.charset = charset
        self.extra_headers = extra_headers
        self.attachments = attachments or []

    @property
    def send_to(self):
        return set(self.recipients) | set(self.bcc or ()) | set(self.cc or ())

    def _mimetext(self, text, subtype='plain'):
        """Creates a MIMEText object with the given subtype (default: 'plain')
        If the text is unicode, the utf-8 charset is used.
        """
        charset = self.charset or 'utf-8'
        return MIMEText(text, _subtype=subtype, _charset=charset)

    def as_string(self):
        """Creates the email"""

        attachments = self.attachments or []

        if len(attachments) == 0 and not self.html:
            # No html content and zero attachments means plain text
            msg = self._mimetext(self.body)
        elif len(attachments) > 0 and not self.html:
            # No html and at least one attachment means multipart
            msg = MIMEMultipart()
            msg.attach(self._mimetext(self.body))
        else:
            # Anything else
            msg = MIMEMultipart()
            alternative = MIMEMultipart('alternative')
            alternative.attach(self._mimetext(self.body, 'plain'))
            alternative.attach(self._mimetext(self.html, 'html'))
            msg.attach(alternative)

        msg['Subject'] = self.subject
        msg['From'] = sanitize_address(self.sender)
        msg['To'] = ', '.join(list(set(sanitize_addresses(self.recipients))))

        msg['Date'] = formatdate(self.date, localtime=True)
        # see RFC 5322 section 3.6.4.
        msg['Message-ID'] = self.msgId

        if self.cc:
            msg['Cc'] = ', '.join(list(set(sanitize_addresses(self.cc))))

        if self.reply_to:
            msg['Reply-To'] = sanitize_address(self.reply_to)

        if self.extra_headers:
            for k, v in self.extra_headers.iteritems():
                msg[k] = v

        for attachment in attachments:
            f = MIMEBase(*attachment.content_type.split('/'))
            f.set_payload(attachment.data)
            encode_base64(f)

            f.add_header('Content-Disposition', '%s;filename=%s' %
                         (attachment.disposition, attachment.filename))

            for key, value in attachment.headers:
                f.add_header(key, value)

            msg.attach(f)

        return msg.as_string()

    def __str__(self):
        return self.as_string()

    def has_bad_headers(self):
        """Checks for bad headers i.e. newlines in subject, sender or recipients.
        """

        reply_to = self.reply_to or ''
        for val in [self.subject, self.sender, reply_to] + self.recipients:
            for c in '\r\n':
                if c in val:
                    return True
        return False

    def is_bad_headers(self):
        from warnings import warn
        msg = 'is_bad_headers is deprecated, use the new has_bad_headers method instead.'
        warn(DeprecationWarning(msg), stacklevel=1)
        return self.has_bad_headers()

    def send(self, connection):
        """Verifies and sends the message."""

        assert self.recipients, "No recipients have been added"

        if not self.sender:
            self.sender = current_app.extensions['mail'].default_sender
            assert self.sender, (
                "The message does not specify a sender and a default sender "
                "has not been configured")

        assert self.sender, "The message does not specify a sender address"

        if self.has_bad_headers():
            raise BadHeaderError

        connection.send(self)

    def add_recipient(self, recipient):
        """Adds another recipient to the message.

        :param recipient: email address of recipient.
        """

        self.recipients.append(recipient)

    def attach(self,
               filename=None,
               content_type=None,
               data=None,
               disposition=None,
               headers=None):
        """Adds an attachment to the message.

        :param filename: filename of attachment
        :param content_type: file mimetype
        :param data: the raw file data
        :param disposition: content-disposition (if any)
        """

        self.attachments.append(
            Attachment(filename, content_type, data, disposition, headers))


class _Mail(object):
    def __init__(self, server, username, password, port, use_tls, use_ssl,
                 default_sender, debug, max_emails, suppress):
        self.server = server
        self.username = username
        self.password = password
        self.port = port
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.default_sender = default_sender
        self.debug = debug
        self.max_emails = max_emails
        self.suppress = suppress


class Mail(object):
    """Manages email messaging

    :param app: Flask instance
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initializes your mail settings from the application settings.

        You can use this if you want to set up your Mail instance
        at configuration time.

        :param app: Flask application instance
        """

        state = _Mail(
            app.config.get('MAIL_SERVER', '127.0.0.1'),
            app.config.get('MAIL_USERNAME'),
            app.config.get('MAIL_PASSWORD'),
            app.config.get('MAIL_PORT', 25),
            app.config.get('MAIL_USE_TLS', False),
            app.config.get('MAIL_USE_SSL', False),
            app.config.get('MAIL_DEFAULT_SENDER'),
            int(app.config.get('MAIL_DEBUG', app.debug)),
            app.config.get('MAIL_MAX_EMAILS'),
            app.config.get('MAIL_SUPPRESS_SEND', app.testing))

        # register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['mail'] = state

    @contextmanager
    def record_messages(self):
        """Records all messages. Use in unit tests for example::

            with mail.record_messages() as outbox:
                response = app.test_client.get("/email-sending-view/")
                assert len(outbox) == 1
                assert outbox[0].subject == "testing"

        You must have blinker installed in order to use this feature.
        :versionadded: 0.4
        """

        if not email_dispatched:
            raise RuntimeError("blinker must be installed")

        outbox = []

        def _record(message, app):
            outbox.append(message)

        email_dispatched.connect(_record)

        try:
            yield outbox
        finally:
            email_dispatched.disconnect(_record)

    def send(self, message):
        """Sends a single message instance. If TESTING is True the message will
        not actually be sent.

        :param message: a Message instance.
        """

        with self.connect() as connection:
            message.send(connection)

    def send_message(self, *args, **kwargs):
        """Shortcut for send(msg).

        Takes same arguments as Message constructor.

        :versionadded: 0.3.5
        """

        self.send(Message(*args, **kwargs))

    def connect(self):
        """Opens a connection to the mail host."""
        app = self.app or current_app
        try:
            return Connection(app.extensions['mail'])
        except KeyError:
            raise RuntimeError("The curent application was not configured with Flask-Mail")


signals = blinker.Namespace()

email_dispatched = signals.signal("email-dispatched", doc="""
Signal sent when an email is dispatched. This signal will also be sent
in testing mode, even though the email will not actually be sent.
""")
