from __future__ import absolute_import
import cgi
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from logging import getLogger
from smtplib import SMTP, SMTPException
import socket
from textwrap import dedent

from webalerts import NotificationException, ConfigurationError


class EmailNotification(object):
    """
    Sends emails to users on matched posts. Although you can specify any SMTP
    server to use to send emails, it is recommended not to use your own mail
    server as many email services refuse to receive emails from unknown sources.
    If you want to send emails using Gmail, set ``host`` to ``'smtp.gmail.com'``,
    ``port`` to 587, ``secure`` to `True`, and ``username`` and ``password``
    to your account.

    Configuration options:

    ``to_addrs``
      List of email addresses to which notifications are sent.

    ``from_addr`` (default: ``'WebAlerts <webalerts@localhost>'``)
      "From" address of notification emails.

    ``host`` (default: `None`)
      Optional host parameter used to create a :py:class:`smtplib.SMTP` instance.

    ``port`` (default: `None`)
      Optional port parameter used to create a :py:class:`smtplib.SMTP` instance.

    ``secure`` (default: `False`)
      Whether the SMTP connection should be secure or not.

    ``username`` (default: `None`)
      SMTP username.

    ``password`` (default: `None`)
      SMTP password.

    ``style`` (default: `see the source`_)
      CSS styles to be placed in in <head>.

    ``template`` (default: `see the source`_)
      HTML template for each posts.

    ``layout`` (default: `see the source`_)
      HTML template for the whole email.

    .. _`see the source`: https://github.com/clee704/WebAlerts/tree/master/webalerts/notifications/email.py

    """

    DEFAULT_VALUES = {
        'from_addr': 'WebAlerts <webalerts@localhost>',
        'host': None,
        'port': None,
        'secure': False,
        'username': None,
        'password': None,
        'template': dedent(u"""\
            <div style="margin-bottom:4em">
              <div>
                <h3 style="font-size:1.25em;margin-bottom:0.4em">
                  <a href="{url}" style="text-decoration: none">{title}</a>
                </h3>
                <small style="color:#666">{published}</small>
              </div>
              <div style="margin-top:1em">{content}</div>
            </div>
        """),
        'layout': dedent(u"""\
            <html>
              <head>
                <style>{style}</style>
              </head>
              <body>
                {body}
              </body>
            </html>
        """),
        'style': "img { max-width: 100%; height: auto; }",
    }

    def __init__(self, config):
        self.config = dict(self.DEFAULT_VALUES)
        self.config.update(config)
        self.logger = getLogger(__name__).getChild(self.__class__.__name__)

    def notify(self, posts):
        if not posts:
            self.logger.info('No posts')
            return
        try:
            emails = self.config['to_addrs']
        except KeyError:
            raise ConfigurationError('Missing required config value to_addrs')
        if len(posts) == 1:
            subject = posts[0].title
        else:
            subject = u'{0} and {1} more'.format(posts[0].title, len(posts) - 1)
        panels = []
        for post in posts:
            panels.append(self.config['template'].format(url=cgi.escape(post.url),
                    title=cgi.escape(post.title),
                    content=post.content_html_safe or cgi.escape(post.content),
                    published=post.published))
        body = '\n'.join(panels)
        html = self.config['layout'].format(style=self.config['style'], body=body)

        try:
            conn = SMTP(self.config['host'], self.config['port'])
            if self.config['secure']:
                conn.ehlo()
                conn.starttls()
            else:
                conn.connect()
            if self.config['username'] and self.config['password']:
                conn.login(self.config['username'], self.config['password'])
            sendmail(conn, self.config['from_addr'], emails, subject, html)
            self.logger.info(u'Notifications sent to %s', emails)
            conn.quit()
        except (socket.error, SMTPException) as e:
            self.logger.warning(u'Failed to send emails')
            raise NotificationException(e)


def sendmail(conn, from_addr, to_addrs, subject, body, body_type='html'):
    encoding = 'UTF-8'
    # Reference: http://mg.pov.lt/blog/unicode-emails-in-python.html
    sender_name, sender_addr = parseaddr(from_addr)
    # We must always pass Unicode strings to Header, otherwise it will
    # use RFC 2047 encoding even on plain ASCII strings.
    sender_name = str(Header(unicode(sender_name), encoding))
    # Make sure email addresses do not contain non-ASCII characters
    sender_addr = sender_addr.encode('ascii')
    msg = MIMEText(body.encode(encoding), body_type, encoding)
    msg['Subject'] = Header(unicode(subject), encoding)
    msg['From'] = formataddr((sender_name, sender_addr))
    msg['To'] = ''
    # TODO call sendmail once by using Bcc if possible
    for to_addr in to_addrs:
        recipient_name, recipient_addr = parseaddr(to_addr)
        recipient_name = str(Header(unicode(recipient_name), encoding))
        recipient_addr = recipient_addr.encode('ascii')
        msg.replace_header('To', formataddr((recipient_name, recipient_addr)))
        conn.sendmail(from_addr, to_addr, msg.as_string())
