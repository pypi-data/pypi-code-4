from tornado import gen, httpclient, ioloop, web
import toro


class CacheEntry(object):
    def __init__(self):
        self.event = toro.Event()
        self.type = self.body = None

cache = {}

class ProxyHandler(web.RequestHandler):
    
    @web.asynchronous
    @gen.coroutine
    def get(self):
        path = self.request.path
        entry = cache.get(path)
        if entry:
            # Block until the event is set, unless it's set already
            yield entry.event.wait()
        else:
            print path
            cache[path] = entry = CacheEntry()

            # Actually fetch the page
            response = yield httpclient.AsyncHTTPClient().fetch(path)
            entry.type = response.headers.get('Content-Type', 'text/html')
            entry.body = response.body
            entry.event.set()

        self.set_header('Content-Type', entry.type)
        self.write(entry.body)
        self.finish()

if __name__ == '__main__':
    print 'Listening on port 8888'
    print
    print 'Configure your web browser to use localhost:8888 as an HTTP Proxy.'
    print 'Try visiting some web pages and hitting "refresh".'
    web.Application([('.*', ProxyHandler)], debug=False).listen(8888)
    ioloop.IOLoop.instance().start()