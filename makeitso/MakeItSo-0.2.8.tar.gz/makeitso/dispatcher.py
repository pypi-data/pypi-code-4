"""
request dispatcher for MakeItSo!
"""

import sys
from handlers import Index
from webob import Request, Response, exc

class Dispatcher(object):

    ### class level variables

    def __init__(self, **kw):

        # request handlers
        self.handlers = [ Index ]

    def __call__(self, environ, start_response):

        # get a request object
        request = Request(environ)

        # get the path 
        path = request.path_info.strip('/').split('/')
        if path == ['']:
            path = []
        request.environ['path'] = path

        # match the request to a handler
        for h in self.handlers:
            handler = h.match(self, request)
            if handler is not None:
                break
        else:
            handler = exc.HTTPNotFound

        # get response
        res = handler()
        return res(environ, start_response)

if __name__ == '__main__':
    from optparse import OptionParser
    from wsgiref import simple_server

    # parse command line options
    parser = OptionParser()
    parser.add_option('-p', '--port', dest='port', default=8080, type='int',
                      help='port to serve on')
    options, args = parser.parse_args()

    # create an app
    app = Dispatcher()

    # serve it!
    server = simple_server.make_server(host=host, port=options.port, app=app)
    server.serve_forever()
