import tornado.ioloop
import tornado.web

from bwikibot.cli import get_wiki, get_secondary_wiki, action

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

application = tornado.web.Application([
    (r"/", MainHandler),
])


@action('serve')
def serve(port):
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
