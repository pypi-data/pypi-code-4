""" :mod:`hedwig.backends.smtp`
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from smtplib import SMTP
from socket import getfqdn

from .base import BaseEmailBackend


class SMTPEmailBackend(BaseEmailBackend):
    """
    SMTP email backend implementation.
    """

    def __init__(self, host='localhost', port=25, username=None, password=None,
                 use_tls=False, **kwargs):
        super(SMTPEmailBackend, self).__init__(**kwargs)
        if isinstance(port, basestring):
            try: 
                port = int(port)
            except ValueError:
                pass
        if not isinstance(host, basestring):
            raise TypeError('host must be a string, not ' + repr(host))
        if not isinstance(port, int):
            raise TypeError('port must be an integer, not ' + repr(port))
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.connection = None

    def open(self):
        super(SMTPEmailBackend, self).open()
        for trial in xrange(5):
            self._open_connection()
            if self.connection:
                break
        if not self.connection:
            raise RuntimeError('cannot open smtp connection') 

    def _open_connection(self):
        local_hostname = getfqdn()
        self.connection = SMTP(self.host, self.port,
                               local_hostname=local_hostname)
        if self.use_tls:
            self.connection.ehlo()
            self.connection.starttls()
            self.connection.ehlo()
        if self.username and self.password:
            self.connection.login(self.username, self.password)

    def close(self):
        if not isinstance(self.connection, SMTP):
            raise RuntimeError('already closed or not opened ever')
        try:
            self.connection.quit()
        except socket.sslerror:
            self.connection.close()
        finally:
            self.connection = None
        super(SMTPEmailBackend, self).close()

    def send_messages(self, email_messages):
        if not email_messages:
            return
        n_sent = 0
        for message in email_messages:
            sent = self._send_message(message)
            if sent:
                n_sent += 1
        return n_sent

    def _send_message(self, email_message):
        if not email_message.recipients:
            return False
        self.connection.sendmail(email_message.from_,
                                 email_message.recipients,
                                 email_message.message().as_string())
        return True
