import asyncore
from multiprocessing import Process

from tornado.web import StaticFileHandler
from tornado import template, ioloop, web

from .smtp import ProxyDebugServer
from .handlers import *
from .settings import *
from .utils.http import split_host_port
from .utils.termcolors import colorize

application = web.Application(
    [
        (r"/", IndexHandler),
        (r"/mail/", MailListHandler),
        (r"/mail/([0-9^/]+)/", MailDetailHandler),
        (r"/mail/all/read/", ReadAllMailHandler),
        (r"/mail/all/delete/", DeleteAllMailHandler),
        (r'/medias/(.*)', StaticFileHandler, {'path': MEDIAS_DIR}),
    ] + EchoSockjsRouter('/inbox'),
    template_loader=template.Loader(TEMPLATES_DIR)
)


def runserver(args):
    http_host, http_port = split_host_port(args.http_bind)
    smtp_host, smtp_port = split_host_port(args.smtp_bind)
    
    print colorize(" * Web server listening at http://%s/" % args.http_bind, fg="green")
    print colorize(" * SMTP server listening at %s" % args.smtp_bind, fg="green")

    ProxyDebugServer(
        (smtp_host, int(smtp_port)),
        queue=MAIN_QUEUE
    )
    try:
        p = Process(target=asyncore.loop)
        p.start()
        # p.join()
        application.listen(int(http_port), address=http_host)
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
