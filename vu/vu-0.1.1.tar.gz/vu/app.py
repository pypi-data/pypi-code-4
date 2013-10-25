import tornado.ioloop
import tornado.web
from tornado import template
from .utils.termcolors import colorize
from .settings import *
from .handlers import *


application = tornado.web.Application([
    (r"/", MainHandler),
], template_loader=template.Loader(TEMPLATES_DIR))


def runserver(port):
    application.listen(port)
    print colorize(" * VU is running on http://127.0.0.1:%s/" % port, fg="green")
    tornado.ioloop.IOLoop.instance().start()
