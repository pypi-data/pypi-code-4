#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009-2012 Etienne Robillard
# All rights reserved.
#
# This file is part of the notmm project.
# More informations @ http://gthc.org/projects/notmm/
"""Mostly Random WSGI Utilities.

Useful for learning and education purposes only. Deploy
in production at your own risks... ;-)
"""

import httplib, hashlib

from wsgiref.headers import Headers as HeaderDct
from datetime import datetime

from exc import *

try:
    import chardet
except ImportError:
    # charset autodetection disabled
    pass

__all__ = (
        'sniff_content_encoding',
        'format_status_int',
        'IterableWSGIResponse', 
        'HTTPResponse',
        'HTTPFoundResponse',
        'HTTPSeeOtherResponse',
        'HTTPRedirectResponse',
        'HTTPNotModifiedResponse',
        'HTTPUnauthorizedResponse',
        'HTTPUnauthorized',
        'HTTPForbiddenResponse',
        'HTTPForbidden',
        'HTTPNotFound',
        )

def bytearray2str(obj, mode='replace'):
    obj.decode('utf8', errors=mode)
    return obj

def sniff_content_encoding(s, default='utf-8'):
    """
    Attempts to detect the character set of a string value ``s`` or 
    ``default`` if the ``chardet`` module is not found.

    """
    try:
        content_encoding = chardet.detect(s)['encoding']
    except (NameError, UnicodeDecodeError):
        content_encoding = default

    return content_encoding

def format_status_int(status_int):
    """
    Returns a string like "200 OK" if the status_int
    numeric value matches something in our internal
    map.
    
    """
    try:
        status_code = httplib.responses[int(status_int)]
    except (TypeError, KeyError):
        status_code = httplib.responses[500]    
    
    return "%s %s" % (status_int, status_code)

class IterableWSGIResponse(object):
    """
    A iterable WSGI object using a simple API inspired by Django
    ``HttpResponse``.
    
    >>>response = IterableWSGIResponse(content='hello world', mimetype='text/plain')
    """
    
    # default headers 
    http_headers = HeaderDct([])
    status_int = None
    environ = {}

    def __init__(
        self, content='', status=None, headers=[], 
        mimetype='text/plain', charset='UTF-8', force_unicode=True
        ):
        """Create a new WSGI response instance.
        
        If ``force_unicode`` is set to ``False``, disable explicit
        multibyte conversion. (Binary files handlers may need this)
        """
        self.mimetype = mimetype
        self.charset = charset
        # XXX workaround the broken unicode stuff in python 2.7.3 
        # note: wsgi require a str though
        if not force_unicode:
            self.content = str(content)
        else:    
            self.content = str(bytearray(content, charset).decode())
        #assert isinstance(content, bytes), type(content)
                
        # 14.15 - Content-MD5 (for integrity checking of
        # the entity-body)
        self.content_hash = str(hashlib.md5(self.content).hexdigest())
        
        # Get the HTTP status code human representation. 
        if status is not None and status >= 200:
            self.status_code = format_status_int(status)
        else:
            # by default attempt to use status_int
            assert isinstance(self.status_int, int)
            self.status_code = format_status_int(self.status_int)
        
        #update status_int
        self.status_int = int(self.status_code[0:4])

        # Provides a basic HTTP/1.1 headers set
        self.http_headers = HeaderDct([
            ('Content-Type', self.content_type),
            ('Content-Length', str(self.content_length)),
            ('Content-MD5', self.content_hash),
            #('ETag', self.content_hash)
            ])
        if len(headers) >= 1:
            for hdr, val in headers:
                if not hdr in self.http_headers:
                    self.http_headers.add_header(str(hdr), (val))
        
        
    # This __str__ silently borrowed from webob.Response.__str__...
    def __str__(self, skip_body=False):
        parts = [str(self.status)]
        parts += map('%s: %s'.__mod__, self.headers)
        if not skip_body and self.content != '':
            parts += ['', self.content]
        #outs = bytearray2str(bytearray(parts))
        return '\n'.join(parts)
    
    def __iter__(self):
        """Return a custom iterator type which iterates over the response."""  
        #XX python mess continue here
        #assert isinstance(wsgi_output, basestring), type(wsgi_output)    
        return iter(self.content)

    app_iter = property(__iter__)

    def __len__(self):
        """Return the Content-length value (type int)."""
         
        return len(self.content)
    
    def __getitem__(self, k):
        """For foo = response['foo'] operations"""
        try:
            v = self.http_headers[k]
        except KeyError:
            return None
        else:
            return v
    
    def __setitem__(self, item, value):
        """For response['foo'] = 'Bar' operations"""
        try:
            self.http_headers[item] = value
        except:
            raise
            
    content_length = property(__len__)
    
    def __call__(self, environ, start_response):
        status_code = self.status_code

        #self.environ.update(environ)
        start_response(status_code, self.headers)
        return self.app_iter

    def get_content_type(self):
        """Returns the current Content-type header"""
        return "%s; charset=%s" % (self.mimetype, self.charset)
    
    content_type = property(get_content_type)

    def write(self, text=''):
        """Writes characters (text) in the input buffer stream (body)"""
        if isinstance(text, basestring): 
            text.encode(self.charset)
        self.content += text
    
    def next(self):
        """ required method for being a proper iterator type """
        chunk = self.app_iter.next()
        #if isinstance(chunk, basestring):
        #    chunk.encode(self.charset)
        return chunk
    
    def has_header(self, value):
        """ return True when ``value`` is found in self.headers (HTTP headers)
        """
        try:
            valueof = self.headers[value]
        except (KeyError, TypeError):
            return False
        else:
            return True
    
    @property        
    def headers(self):
        return [(hdr, str(val)) for hdr, val in self.http_headers.items()]

    @property
    def status(self):
        return self.status_int

class HTTPResponse(IterableWSGIResponse):
    """HTTP 200 (OK)"""
    status_int = 200

class HTTPFoundResponse(HTTPResponse):
    """HTTP 302 (Found)
    
    Requires one param: 
    * location: a URI string.
    """
    
    status_int = 302
    
    def __init__(self, location, **kwargs):
        kwargs['status'] = str(self.status_int)
        # Displays a short message to the user with a link to
        # the given resource URI
        kwargs['content'] = '''\
        <p>Click here to follow this redirect: <a href=\"%s\">Link</a></p>'''%location
        super(HTTPFoundResponse, self).__init__(**kwargs)
        
        self.location = location     # location to redirect to

        #self.initial_kwargs = kwargs 
        self.http_headers['Location'] = location
        self.http_headers['Cache-Control'] = 'no-cache' # Prevent caching redirects

    def __call__(self, env, start_response):
        start_response(self.status_code, self.headers)
        return self.app_iter

HTTPRedirectResponse = HTTPFoundResponse # alias

class HTTPSeeOtherResponse(HTTPFoundResponse):
    """HTTP 303 (See Other)"""
    status_int = 303

class HTTPNotModifiedResponse(HTTPResponse):
    """HTTP 304 (Not Modified)"""
    status_int = 304

    def __init__(self, *args, **kwargs):
        super(HTTPNotModifiedResponse, self).__init__(*args, **kwargs)
        
        self.http_headers['Date'] = datetime.now().ctime()
            

        del self.http_headers['Content-Type']
    
        self.content = '';


class HTTPUnauthorizedResponse(HTTPResponse):
    """HTTP 401 (Unauthorized)"""
    status_int = 401

HTTPUnauthorized = HTTPUnauthorizedResponse

class HTTPForbiddenResponse(HTTPResponse):
    """HTTP 403 (Forbidden)"""
    status_int = 403

HTTPForbidden = HTTPForbiddenResponse

class HTTPNotFound(HTTPResponse, HTTPClientError):
    """HTTP 404 (Not Found)"""
    status_int = 404
