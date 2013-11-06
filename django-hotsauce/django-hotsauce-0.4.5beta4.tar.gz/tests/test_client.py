import os
import sys

#from cStringIO import StringIO

class TestApp(object):
    """basic configuration options for the test application"""
    
    # A minimal environment for WSGI testing
    default_wsgi_env = {
        #'HTTP_COOKIE':  self.cookies.output(header='', sep='; '),
        #'PATH_INFO':    '',
        #'QUERY_STRING': '',
        #'REMOTE_ADDR':  '127.0.0.1',
        #'REQUEST_METHOD':    'GET',
        #'SCRIPT_NAME':       '',
        #'SERVER_NAME':       'testserver',
        #'SERVER_PORT':       '80',
        #'SERVER_PROTOCOL':   'HTTP/1.1',
        'wsgi.version':      (1, 0),
        'wsgi.url_scheme':   'http',
        'wsgi.errors':       sys.stderr,
        'wsgi.multiprocess': True,
        'wsgi.multithread':  False,
        'wsgi.run_once':     False,
        'wsgi.input':        sys.stdin
    }

    
    def __init__(self, wsgi_app, environ={}, method='GET'):
        self.wsgi_app = wsgi_app
        try:
            environ.update(getattr(wsgi_app, 'environ', self.default_wsgi_env))
        except AttributeError:
            raise
        else:
            self.environ = environ
            self.environ['REQUEST_METHOD'] = method
            # init the base HTTPRequest instance
            try:
                self.wsgi_app.registerWSGIHandlers(
                    wsgi_app.settings.CUSTOM_ERROR_HANDLERS
                    )
                self.wsgi_app.init_request(self.environ)
                self.request = self.wsgi_app.request
            except AttributeError:
                # Error initializing the WSGI request
                self.request = None

class TestClient(TestApp):

    def __init__(self, wsgi_app, **kwargs):
        super(TestClient, self).__init__(wsgi_app, **kwargs)
    
    def get(self, path_url, **kwargs):
        """GET"""
        if 'status' in kwargs:
            # If debugging, verify if status matches the returned status
            # code.
            status_int = kwargs['status']
            assert isinstance(status_int, int), 'expected a integer value'
        
        response = self.wsgi_app.get_response(path_url)
        return response

    def put(self, path_url):
        """PUT"""
        # TODO: Add a new permanent URI object in the urlmap.
        raise NotImplementedError
    
    def post(self, path_url, request=None, data={}):
        """POST"""

        post_data = data
        if request is not None:
            assert request.method == 'POST', request.method
            post_data.update(self.request.POST)    
        request.environ['HTTP_METHOD'] = 'POST'    
        response = self.wsgi_app.get_response(path_url, request=request, method='POST', data=post_data)
        return response

    def head(self, path_url):
        raise NotImplementedError

    def delete(self, path_url, **kwargs):
        """Delete a URI in the urlmap (mutable object)."""
        raise NotImplementedError
    
    def etags(self, path_url):
        """Obtain the ETag value if available for a given URI"""
        raise NotImplementedError

