import os
import logging
import threading
from mimetypes import guess_type

import tornado.ioloop
import tornado.web
import tornado.websocket


class MainHandler(tornado.web.RequestHandler):

    def initialize(self, path):
        self.root_path = path

    def get(self, url):
        path = os.path.join(self.root_path, url.lstrip('/'))
        if os.path.isdir(path):
            index = os.path.join(path, 'index.html')
            if os.path.isfile(index):
                self._serve_html(index)
            else:
                # serve directory
                self._serve_folder(path)

        elif os.path.isfile(path):
            mime, encoding = guess_type(path)
            if mime == 'text/html':
                self._serve_html(path)
            else:
                with open(path, 'rb') as f:
                    if mime:
                        self.set_header('Content-Type', mime)
                    if encoding:
                        self.set_header('Content-Encoding', encoding)
                    self.write(f.read())

    def _serve_html(self, path):
        self.set_header('Content-Type', 'text/html')
        with open(path) as f:
            data = f.read()
            head, body = data.split('<head>')
            self.write(head)
            self.write('<head>')
            self.write('''<script>
                var source = new EventSource('/termite_events');
                source.addEventListener('message', function(e) {
                    if(e.data == 'reload')
                        window.location.reload(true);
                    else if (e.data == 'close')
                        source.close();
                }, false);
                </script>''')
            self.write(body)

    def _serve_folder(self, path):
        self.set_header('Content-Type', 'text/html')

        relpath = '/' + os.path.relpath(path, self.root_path).lstrip('.')
        self.write('<h1>Directory listing for {}</h1><hr>'.format(relpath))

        self.write('<ul>')
        for name in os.listdir(path):
            self.write('<li>')
            slash = '/' if os.path.isdir(os.path.join(path, name)) else ''
            self.write('<a href="{relpath}/{name}">{name}{slash}</a>'.
                       format(relpath=relpath, name=name, slash=slash))
            self.write('</li>')

        self.write('</ul><hr>')


class SSEHandler(tornado.web.RequestHandler):

    connections = set()

    def set_default_headers(self):
        self.set_header('Content-Type', 'text/event-stream')
        self.set_header('Cache-Control', 'no-cache')

    @classmethod
    def send_reload_events(cls):
        for connection in cls.connections.copy():
            connection.send_reload_event()

    def send_reload_event(self):
        self.write('data: reload\n\n')
        self.flush()
        self.finish()
        self.connections.discard(self)

    @classmethod
    def send_close_events(cls):
        for connections in cls.connections:
            connections.send_close_event()

    def send_close_event(self):
        self.write('data: close\n\n')
        self.flush()
        self.finish()

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        SSEHandler.connections.add(self)


def start_tornado(path):
    application = tornado.web.Application([
        (r'/termite_events', SSEHandler),
        (r'(.*)', MainHandler, dict(path=path)),
    ])

    application.listen(8888)

    logging.info("Starting Torando")
    tornado.ioloop.IOLoop.instance().start()
    logging.info("Tornado finished")


def stop_tornado():
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_callback(lambda x: x.send_close_events(), SSEHandler)
    ioloop.add_callback(lambda x: x.stop(), ioloop)
    logging.info("Asked Tornado to exit")


class Server:
    def __init__(self, path=None):
        self.t = threading.Thread(target=start_tornado, kwargs={'path': path})
        self.t.start()

    def stop(self):
        stop_tornado()
        self.t.join()
