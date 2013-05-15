# -*- mode: python; coding: utf-8 -*-

"""logging handlers
.. moduleauthor:: Arco Research Group
"""

import sys
import time

import logging
from logging.handlers import SMTPHandler

import warnings
warnings.filterwarnings('ignore')


try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


class Account(object):
    def __init__(self, username, password=None):
        self.username = username
        self.password = password

    @property
    def credentials(self):
        return self.username, self.password


class Server(object):
    def __init__(self, hostname, port, ssl=False):
        self.hostname = hostname
        self.port = port
        self.ssl = ssl

    @property
    def socket(self):
        return self.hostname, self.port


class SMTP_SSLHandler(SMTPHandler):
    """
    A handler class which sends an SMTP email for each logging event.
    """

    def __init__(self, toaddrs, mailhost=None, fromaddr=None,
                 subject='', credentials=None, ssl=False):

        SMTPHandler.__init__(self, mailhost, fromaddr,
                             toaddrs, subject, credentials)

        self.ssl = ssl

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib
            from email.utils import formatdate

            port = self.mailport or smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = u"From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                self.fromaddr,
                str.join(",", self.toaddrs),
                self.getSubject(record),
                formatdate(),
                unicode(self.format(record), 'utf-8'))

            if self.ssl:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

            if self.username:
                smtp.login(self.username, self.password)

            smtp.sendmail(self.fromaddr, self.toaddrs, msg.encode('utf-8'))
            smtp.close()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class SimpleSMTP_SSLHandler(SMTP_SSLHandler):
    def __init__(self, toaddrs, subject='', sender=None, server=None):
        super(SimpleSMTP_SSLHandler, self).__init__(
            toaddrs     = toaddrs,
            subject     = subject,
            fromaddr    = sender.username,
            credentials = sender.credentials,
            mailhost    = server.socket,
            ssl         = server.ssl)


# From: http://code.activestate.com/recipes/498158-logging-to-a-jabber-account/
class JabberHandler(logging.Handler):
    def __init__(self, sender, to, logger=None, lazy=True):
        """
        log: is a creator logger
        """

        self.sender = sender
        self.to_id = to
        self.logger = logger or logging.getLogger("JabberHandler")
        self.logger.propagate = False
        self.logger.addHandler(NullHandler())
        self.connected = False

        super(JabberHandler, self).__init__()

        if not lazy:
            self.connect()

    def connect(self):
        if self.connected:
            return

        self.xmpp = __import__('xmpp')

        jid = self.xmpp.protocol.JID(self.sender.username)
        self.user = jid.getNode()
        self.server = jid.getDomain()

        self.logger.debug("Connecting %s@%s" % (self.user, self.server))

        self.conn = self.xmpp.Client(self.server, debug=[])
        conres = self.conn.connect()

        if not conres:
            self.logger.error("Unable to connect to server %s!" % self.server)
            return

        if conres != 'tls':
            self.logger.warning("Unable to estabilish secure connection - TLS failed!")

        authres = self.conn.auth(self.user, self.sender.password,
                                 resource=self.server)

        if not authres:
            self.logger.error("Unable to authorize on %s - check login/password." % self.server)
            return

        if authres != 'sasl':
            self.logger.warning("Unable to perform SASL auth os %s. Old authentication method used!" % self.server)

        self.conn.sendInitPresence(requestRoster=0)
        self.connected = True

    def emit(self, record):
        if not self.connected:
            self.connect()

#        try:
        self.conn.send(\
            self.xmpp.protocol.Message(
                to   = self.to_id,
                body = self.format(record)))
#        except:
#            self.handleError(record)


class NotifyHandler(logging.Handler):
    'A logging Handler to show messages using notification daemon'
    ICONS = {
        logging.CRITICAL: 'gtk-cancel',
        logging.ERROR:    'gtk-dialog-error',
        logging.WARNING:  'gtk-dialog-warning',
        logging.INFO:     'gtk-dialog-info',
        logging.DEBUG:    'gtk-execute',
        }

    notification = None

    def emit(self, record):
        try:
            from gi.repository import Notify, GLib
            Notify.init("app")
        except ImportError:
            sys.stderr.write('Error: NotifyHandler requires gir1.2-notify\n')
            raise

        message = record.getMessage()
        try:
            summary, full = message.split('\n', 1)
        except ValueError:
            summary, full = message, ''
        icon = NotifyHandler.ICONS.get(record.levelno, 'gtk-dialog-question')

        if self.notification:
            time.sleep(0.5)
            self.notification.close()

        self.notification = Notify.Notification.new(summary, full, icon=icon)
        self.notification.set_hint("transient", GLib.Variant.new_boolean(True))
        self.notification.set_urgency(urgency=Notify.Urgency.NORMAL)
        self.notification.set_timeout(1)
        self.notification.show()


class ColorFormatter(logging.Formatter):
    """
    A formatter wich adds support on logging for colors.
    """

    codes = {\
        None:       (0,  0,   0),  # default
        'DEBUG':    (0,  0,   2),  # gray
        'INFO':     (0,  0,   0),  # normal
        'WARNING':  (38, 5, 208),  # orange
        'ERROR':    (0,  1,  31),  # red
        'CRITICAL': (0,  1, 101),  # black with red background
        }

    def color(self, level=None):
        return (chr(27) + '[%d;%d;%dm') % self.codes[level]

    def format(self, record):
        retval = logging.Formatter.format(self, record)
        return self.color(record.levelname) + retval + self.color()


class CapitalLoggingFormatter(logging.Formatter):
    """
    define variable "levelcapital" for message formating. You can do things like:
    [EE] foo bar
    """

    def format(self, record):
        record.levelcapital = record.levelname[0] * 2
        return logging.Formatter.format(self, record)
