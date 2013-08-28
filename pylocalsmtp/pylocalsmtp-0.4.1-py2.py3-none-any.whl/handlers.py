from Queue import Empty
from tornado import ioloop, web
# from tornado.escape import json_encode
from sockjs.tornado import SockJSRouter, SockJSConnection
from multiprocessing import Queue
from .models import Mail


__all__ = (
    'MAIN_QUEUE', 'IndexHandler', 'MailListHandler',
    'ReadAllMailHandler', 'DeleteAllMailHandler',
    'MailDetailHandler', 'EchoConnection', 'EchoSockjsRouter'
)

MAIN_QUEUE = Queue()


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")


class MailListHandler(web.RequestHandler):
    def get(self):
        mails = Mail.select()
        out = {
            "object_list": [m.dict() for m in mails],
            "count": mails.count()
        }
        self.write(out)


class MailDetailHandler(web.RequestHandler):
    def get(self, mail_id):
        mail = Mail.get(Mail.id == mail_id)
        mail.read_mail()
        self.write(mail.dict())


class ReadAllMailHandler(web.RequestHandler):
    def post(self):
        mails = Mail.select().where(Mail.read == 0)
        # TODO : find with peewee how to perform
        # update actions on a queryset
        read_ids = []
        for mail in mails:
            mail.read_mail()
            read_ids.append(mail.id)
        self.write({'ok': True, 'read_ids': list(set(read_ids))})


class DeleteAllMailHandler(web.RequestHandler):
    def post(self):
        Mail.drop_table()
        Mail.create_table()
        self.write({'ok': True})


## SOCKJS HANDLERS
## ---------------

class EchoConnection(SockJSConnection):
    def on_message(self, msg=None):
        self.loop = ioloop.PeriodicCallback(self._send_mail, 999)
        self.loop.start()

    def _send_mail(self):
        while True:
            try:
                msg = MAIN_QUEUE.get(block=False)
                self.send(msg.dict())
            except Empty:
                break

    def on_close(self):
        self.loop.stop()


def EchoSockjsRouter(prefix):
    return SockJSRouter(EchoConnection, prefix).urls
