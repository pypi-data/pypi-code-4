#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import urllib
import sys
import cgi

from django.http import QueryDict
from notmm.utils.markup import formutil
from notmm.utils.django_settings import LazySettings


__all__ = ['HTTPRequest']

class HTTPRequest(object):
    """A generic HTTP request object."""
    
    wsgi_environ = {
        'wsgi.version':      (1, 0),
        'wsgi.url_scheme':   'http',
        'wsgi.errors':       [],
        'wsgi.multiprocess': True,
        'wsgi.multithread':  False,
        'wsgi.run_once':     False,
        'wsgi.input':        None, 
        'django.settings':   LazySettings()
    }

    def __init__(self, environ={}):
        """provide a generic environment for HTTP requests"""
        

        if isinstance(environ, dict):
            self.wsgi_environ.update(environ)
        
        #self._environ['REQUEST_METHOD'] = method

        # parse the query string
        if 'QUERY_STRING' in environ:
            self.query_args =  QueryDict(environ['QUERY_STRING'])
        else:
            self.query_args = {}

    def get_remote_user(self):
        '''Subclasses should override this method to retrieve a User storage class
        programmatically.'''
        # Adds a copy of the user settings to the
        # session store
        user = self.environ.get('REMOTE_USER', None)
        return user

    @property
    def user(self):
        """Returns the current user as defined in environ['REMOTE_USER'] or
        None if not set"""
        return self.get_remote_user()

    def get_full_path(self):
        """Return the value of PATH_INFO, a web browser dependent
        HTTP header, or None if the value is not set"""

        try:
            p = urllib.unquote_plus(self.environ['PATH_INFO'])
        except KeyError:
            # invalid CGI environment
            return None
        return p    
            
    def get_POST(self, idx=0):
        """Extracts data from a POST request
        Returns a dict instance with extracted keys/values pairs."""
        if not (self.method == 'POST' or 'wsgi.input' in self.environ):
            return {}
        #import pdb; pdb.set_trace()
        fs_environ = self.environ.copy()
        return formutil.MultiDict(fs_environ).raw_post_data

    # extra public methods borrowed from Django
    def is_ajax(self):
        """check if the http request was transmitted with asyncronous (AJAX) transport"""
        if 'HTTP_X_REQUESTED_WITH' in self.environ:
            if self.environ['HTTP_X_REQUESTED_WITH'] is 'XMLHttpRequest':
                return True
        #print 'not ajax'        
        return False        

    
    def is_secure(self):
        return bool(self.environ.get("HTTPS") == "on")
    
    def get_session(self):
        return getattr(self, '_session')
    
    @property
    def method(self):
        return str(self.environ.get('REQUEST_METHOD'))
    
    @property
    def POST(self):
        return self.get_POST()

    @property
    def GET(self):
        return getattr(self, 'query_args', ())

    @property
    def remote_user(self):
        return self.get_remote_user()
    
    @property
    def environ(self):
        return getattr(self, 'wsgi_environ')

    path_url = property(get_full_path)
