from peewee import *
from .helpers import DB
from tornado.escape import linkify, xhtml_unescape


class Mail(Model):
    mail_from = CharField()
    mail_to = CharField()
    subject = CharField()
    sent_date = DateTimeField()
    headers = TextField()
    body = TextField()
    read = BooleanField(default=False)

    class Meta:
        database = DB
        order_by = ('-sent_date', )

    @property
    def body_html(self):
        b = self.body
        b = b.replace("\n", "<br />")
        b = xhtml_unescape(linkify(b, extra_params='target="_blank"'))
        return b

    @property
    def headers_html(self):
        h = self.headers.replace("\n", "<br />")
        return h

    def dict(self):
        """
        The use of __dict__ can be magic and
        contains uneccessary datas.
        I prefer re-write the object dictionnary
        """
        return {
            "id": self.id,
            "mail_from": self.mail_from,
            "mail_to": self.mail_to,
            "subject": self.subject,
            "sent_date": self.sent_date.strftime('%Y-%m-%d %H:%M:%S'),
            "headers": self.headers,
            "headers_html": self.headers_html,
            "body": self.body,
            "body_html": self.body_html,
            "read": self.read,
        }

try:
    Mail.create_table()
except:
    pass
