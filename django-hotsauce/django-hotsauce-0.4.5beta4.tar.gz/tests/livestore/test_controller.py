import os, sys

from notmm.controllers.wsgi import WSGIController
from notmm.utils.cookiestore import CookieStore
from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIHandler, WSGIRequest

#from pprint import pprint as pp

#from threading import Lock
#initLock = Lock()

def resolve(resolver, path_url):# match the location to a view or callable
    try:
        callback, args, kwargs = resolver.resolve(path_url)
        response = callback(request, *args, **kwargs)
    except:
        raise
    else:
        return response

class SatchmoController(WSGIController):

    #request_class = WSGIRequest
    #request_middlewares = []

    class SatchmoCookieStore(CookieStore):
        from django.contrib.auth.models import AnonymousUser
        user = AnonymousUser()

    def __init__(self, *args, **kwargs):
        super(SatchmoController, self).__init__(*args, **kwargs)
        self._debug = True
        self._maintainer_mode = (self._debug != False)
        self.locals.session = self.SatchmoCookieStore()
        
        # Set up middleware if needed.
        #if self._request_middleware is None:
        #    self.initLock.acquire()
        #    # Check that middleware is still uninitialised.
        #    if self._request_middleware is None:
        #        self.load_middleware()
        #    self.initLock.release() 
    
    def process_request(self, env):
        super(SatchmoController, self).process_request(env)

        if not hasattr(self.request, 'session'): #FIXME
            self.request.session = self.locals.session
            
        
        if self._debug:
            assert self.request.path == env['PATH_INFO'], 'wsgi sanity check failed, expected %r' % self.request.path
            assert self.request.session != None

        self.request.user = self.request.session.user
        self.request.urlconf = self.urlconf
        
    
    def get_response(self, env, start_response):
        return super(SatchmoController, self).get_response(env, start_response)
        #wsgi_app = WSGIHandler()
        #wsgi_app.load_middleware()
        #wsgi_app._request = self.get_request()
        

    def application(self, env, start_response):
        return self.get_response(env, start_response)
            
