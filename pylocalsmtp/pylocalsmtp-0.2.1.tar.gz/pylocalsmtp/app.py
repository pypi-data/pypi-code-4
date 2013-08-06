import asyncore
from smtpd import parseargs
from multiprocessing import Process

from tornado.web import StaticFileHandler
from tornado import template, ioloop, web

from .smtp import ProxyDebugServer
from .handlers import *
from .settings import *

application = web.Application(
    [
        (r"/", IndexHandler),
        (r"/mail/", MailListHandler),
        (r"/mail/([0-9^/]+)/", MailDetailHandler),
        (r'/medias/(.*)', StaticFileHandler, {'path': MEDIAS_DIR}),
    ] + EchoSockjsRouter('/inbox'),
    template_loader=template.Loader(TEMPLATES_DIR)
)


def runserver():
    PORT = 8888
    print "Web server listening at http://127.0.0.1:%s/ ...\n" % PORT
    options = parseargs()
    proxy = ProxyDebugServer(
        (options.localhost, 1025),
        (options.remotehost, options.remoteport),
        queue=MAIN_QUEUE
    )
    try:
        p = Process(target=asyncore.loop)
        p.start()
        # p.join()
        application.listen(PORT)
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    runserver()
