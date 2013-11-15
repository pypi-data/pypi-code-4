#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import re
from formv.validators.base import VLength
from formv.exception import Invalid
from formv.utils import extract_text as _
from formv.utils.compat import urlparse, urlopen, URLError, PY2
from formv.utils.encoding import decode, encode

__all__ = ('VEmail','VPassword','VRegex','VString','VText','VURL','VUserAgent',)

class VString(VLength):
    def _validate(self, value):
        value = VLength._validate(self, value)
        return str(decode(encode(value)))


class VRegex(VString):
    def __init__(self, regex, flags=0, **kw):
        VString.__init__(self, **kw)
        self.regex = regex
        self.flags = flags
        self.regex = re.compile(self.regex, self.flags)

    def _validate(self, value):
        value = VString._validate(self, value)
        self.messages.update({'invalid': _('Invalid input')})

        if not self.regex.search(value):
            raise Invalid(self.message('invalid'), value)
        return value


class VText(VRegex):
    def __init__(self, **kw):
        VRegex.__init__(self, r"^[a-zA-Z_\-0-9]*$", 0, **kw)
        
        
class VEmail(VString):
    def __init__(self, restricted_domains=[], **kw):
        kw.update({'strip': True}) 
        VString.__init__(self, **kw)
        self.restricted_domains = restricted_domains        

    def _validate(self, value):
        value = VString._validate(self, value)
        self.messages.update({'invalid': _('Invalid email address')})
        
        for d in self.restricted_domains:
            if value.endwith(d):
                raise Invalid(self.message('invalid'), value)
            
        user = re.compile(r"^[\w!#$%&'*+\-/=?^`{|}~.]+$")
        domain = re.compile(r'''
            ^(?:[a-z0-9][a-z0-9\-]{,62}\.)+        # subdomain
            (?:[a-z]{2,63}|xn--[a-z0-9\-]{2,59})$  # top level domain
        ''', re.I | re.VERBOSE)

        try:
            u, d = value.split('@', 1)
        except ValueError:
            raise Invalid(self.message('invalid'), value)
        if not user.search(u):
            raise Invalid(self.message('invalid'), value)
        if not domain.search(d):
            raise Invalid(self.message('invalid'), value)
        return value

    
class VPassword(VString):
    def __init__(self, special_chars=0, **kw):
        kw.update({'strip': True, 'required': True})
        VString.__init__(self, **kw)
        self.special_chars = int(special_chars)
    
    def _validate(self, value):
        value = VString._validate(self, value)
        self.messages.update({
            'special_chars': _('You must include at least %(schars)i special characters in your password'), 
        })                             

        special_chars = re.compile(r'[a-zA-Z]').sub('', value)
        if len(special_chars) < self.special_chars: 
            msg = self.message('special_chars', schars=self.special_chars)
            raise Invalid(msg, value)  
        return value       


class VURL(VString):
    def __init__(self, connect=False, **kw):
        VString.__init__(self, **kw)        
        self.connect = connect
                
    def _validate(self, value):        
        value = VString._validate(self, value)
        self.messages.update({
            'invalid': _('Invalid URL'),
            'url_error': _('An error occurred when trying to access the URL: %(error)s'),            
            'not_found': _('Page could not be found'),
            'bad_status': _('Server returned a bad status code: (%(status)s)'),
        })

        scheme, netloc, path, params, query, fragment = urlparse.urlparse(value)
        
        if scheme not in ('http','https','ftp'):
            raise Invalid(self.message('invalid'), value)
        
        if not netloc:
            raise Invalid(self.message('invalid'), value)

        if path and not '/' in path:
            raise Invalid(self.message('invalid'), value)
        
        if PY2:
            netloc = unicode(netloc)
        value = str(urlparse.urlunparse((scheme, decode(netloc.encode('idna')),
                                         path, params, query, fragment)))
        if self.connect:
            try:
                r = urlopen(value)
                if r.code == 404:
                    raise Invalid(self.message('not_found'), value)
                if not 200 <= r.code < 500:            
                    raise Invalid(self.message('bad_status', status=r.code), value)
            except URLError as e:
                raise Invalid(self.message('url_error', error=e), value)
        return value


class VUserAgent(VString):
    """ not_allowed should be a subset of allowed """
    
    def __init__(self, allowed=None, not_allowed=None, **kw):
        VString.__init__(self, **kw)        
        self.allowed = allowed or ['^MOZILLA.*','^SEAMONKEY.*',
                                   '^GOOGLEBOT.*','^YAHOOSEEKER.*',
                                   '^MSNBOT.*',]        
        self.not_allowed = not_allowed or ['^MOZILLA.*?MSIE 6.*',]
        
        self.allowed = [re.compile(ua) for ua in self.allowed]        
        self.not_allowed = [re.compile(ua) for ua in self.not_allowed]
                
    def _validate(self, value):        
        value = VString._validate(self, value)
        self.messages.update({'not_allowed': _('User agent %(ua)s not allowed'),})
        
        allowed = not_allowed = False
        for ua in self.allowed:
            if ua.search(value.upper()):
                allowed = True
                break 
    
        for ua in self.not_allowed:
            if ua.search(value.upper()):
                not_allowed = True
                break 
        
        if not allowed or not_allowed:
            raise Invalid(self.message('not_allowed', ua=value), value)
        
        return value
    