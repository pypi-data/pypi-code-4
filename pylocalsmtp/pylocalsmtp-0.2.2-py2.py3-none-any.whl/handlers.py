from Queue import Empty
from tornado import ioloop, web
# from tornado.escape import json_encode
from sockjs.tornado import SockJSRouter, SockJSConnection
from multiprocessing import Queue
from .models import Mail


__all__ = (
    'MAIN_QUEUE', 'IndexHandler', 'MailListHandler',
    'MailDetailHandler', 'EchoConnection', 'EchoSockjsRouter'
)

MAIN_QUEUE = Queue()


class IndexHandler(web.RequestHandler):
    def get(self):
        mails = Mail.select()
        self.render("index.html", mails=mails)


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
        mail.read = True
        mail.save()
        self.write(mail.dict())


## SOCKJS HANDLERS
## ---------------

class EchoConnection(SockJSConnection):
    def on_message(self, msg=None):
        self.loop = ioloop.PeriodicCallback(self._send_mail, 999)
        self.loop.start()

    def _send_mail(self):
        try:
            msg = MAIN_QUEUE.get(block=False)
            print "I GOT SOMETHING !!"
            self.send(msg.dict())
        except Empty:
            pass

    def on_close(self):
        self.loop.stop()


def EchoSockjsRouter(prefix):
    return SockJSRouter(EchoConnection, prefix).urls
