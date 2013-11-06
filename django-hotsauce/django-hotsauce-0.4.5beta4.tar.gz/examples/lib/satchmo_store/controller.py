import os, sys
from notmm.controllers.wsgi import WSGIController
from notmm.utils.cookiestore import CookieStore
from django.core.handlers.wsgi import WSGIHandler

#from threading import Lock
#initLock = Lock()

class SatchmoController(WSGIController):

    #request_class = WSGIRequest
    request_middlewares = [WSGIHandler()]

    class SatchmoCookieStore(CookieStore):
        from django.contrib.auth.models import AnonymousUser
        user = AnonymousUser()

    def __init__(self, *args, **kwargs):
        super(SatchmoController, self).__init__(*args, **kwargs)
        
    def process_request(self, env):
        super(SatchmoController, self).process_request(env)

        if not hasattr(self.request, 'session'): #FIXME
            self.request.session = self.SatchmoCookieStore()
        
        #user = self.request.session.user    
        #if user is not None:
        #    self.request.user = user

        if self._debug:
            assert self.request.path == env['PATH_INFO'], 'wsgi sanity check failed, expected %r, got %r' % (self.request.path, env['PATH_INFO'])
            assert self.request.session != None

        self.request.urlconf = self.urlconf
    
    def get_response(self, env, start_response):
        for app in self.request_middlewares:
            app = app(env, start_response)
        return app
    
    def application(self, env, start_response):
        try:
            return self.get_response(env, start_response)
        except:
            return self.process_exception(env, start_response)

