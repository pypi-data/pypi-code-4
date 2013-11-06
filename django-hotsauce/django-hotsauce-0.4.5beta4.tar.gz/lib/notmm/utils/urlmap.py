#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved
# <LICENSE=ISC>
"""A class-based URL resolving module for Django.

* RegexURLMap:
    Provides a easy-to-use API to build logical groups of callbacks 
    to URIs.
* RegexURLMapException: 
    Reserved for future uses; Exception handling of ``RegexURLMap`` instances.
* include, patterns, and url functions are provided as helpers while upgrading from Django to RegexURLMap.

"""
from django_compat import RegexURLPattern, RegexURLResolver
from django.utils.importlib import import_module
import re

__all__ = ['RegexURLMapException', 'RegexURLMap', 'url', 'include']

include = lambda urlconf: [urlconf]

def url(regex, view, kwargs=None, name=None, prefix=''):

    if isinstance(view, (tuple, list)):
        # For include(...) processing.
        return RegexURLResolver(regex, view[0], kwargs, app_name=name, namespace=name)
    else:
        if isinstance(view, str):
            if not view:
                raise RegexURLMapException('Empty URL pattern view name not permitted (for pattern %r)' % regex)
            if prefix:
                view = prefix + '.' + view
        return RegexURLPattern(regex, view, kwargs, name)

class RegexURLMapException(Exception):
    """
    Generic error manipulating a ``RegexURLMap`` object.
    
    """

class RegexURLMap(object):
    """
    Add or create a list of available ``RegexURLPattern`` instances.
 
    Usage ::

    .. coding: python

        >>> from notmm.controllers.routing import RegexURLMap
        >>> urlpatterns = RegexURLMap(label='default')
        >>> print repr(urlpatterns)
        <RegexURLMap: 'default'> 
        >>> urlpatterns.add_routes('myapp.views', ...) # default
        >>> urlpatterns.include(foo.bar.urls) # include urls from another module
    """

    def __init__(self, label='yadayada', verbosity=1):
        self.routes = []
        self.label = label # Label for this urlmap object
        self.debug = (verbosity >= 2)
    
    def __len__(self):
        # Return the number of routes available for this urlmapper
        return len(self.routes)

    def __repr__(self):
        return "<RegexURLMap: %r>" % self.label
    
    def add_routes(self, callback_prefix='', *args):
        """
        Adds a sequence of ``RegexURLPattern`` instances for routing
        valid HTTP requests to a WSGI callback function.

        Unlike the original ``include`` hook provided in Django, this 
        method can be used to create logical groups of routes within the
        same urls.py file. 
        
        """
        self.callback_prefix = callback_prefix

        for t in args:
            self.makeroute(t)

    def makeroute(self, t):
        """Connect a wsgi app to a URI. Invoked by ``add_routes`` to
        flattenize all urls.py into a immutable list of URIs."""
        route = None
        if isinstance(t, (list, tuple)):
            #assert len(t) >= 2, t
            try:
                regex, view, kwargs = t
            except (ValueError, IndexError):
                regex, view = t
                kwargs = {}
            # create a new RegexURLPattern object
            route = url(regex, view, kwargs=kwargs, prefix=self.callback_prefix)
        elif isinstance(t, RegexURLPattern):
            t.add_prefix(self.callback_prefix)
            route = t
        
        try:
            if route:
                self.routes.append(route)
        except AttributeError:
            raise RegexURLMapException('Cannot add more routes after commit().')


    def include(self, urlobj, prefix='', callback_prefix='',
        attr_name='urlpatterns'):
        """Includes urls found in module ``urlobj``.
        
        """
        objtype = type(urlobj)
        if isinstance(urlobj, tuple):
            urls = urlobj[0] # handle admin.site.urls
        #elif objtype in (str, basestring):
        else:
            # urlmap.include('foo.bar.urls', ...)
            urlconf = import_module(urlobj)
            #print "urlconf=%r"%urlconf
            urls = getattr(urlconf, attr_name)
        #else:
        #    # not a string type, neither a sequence, so its the default
        #    # behavior (urlconf)
        #    try:
        #        urls = getattr(urlobj, attr_name)
        #    except AttributeError:
        #        #assert attr_name in urlobj.__dict__, 'Not a valid urls.py file.'
        #        raise RegexURLMapException('urlconf missing attribute %r' % attr_name)
        
        self.callback_prefix = callback_prefix

        for instance in urls:
            pattern = prefix + instance.regex.pattern[1:]
            try:
                instance.__dict__['regex'] = re.compile(pattern)
            except re.error:
                #   already included pattern, skip and continue parsing
                #   the remaining patterns.
                continue
            #self.add_routes(callback_prefix, *urls)
            self.makeroute(instance)

    #merge = staticmethod(include)
    
    def commit(self):
        """Freeze the routes. (cannot add anymore)"""
        self.routes = frozenset([item for item in self.routes])
        #self._commit_flag = True
        if self.debug:
            #print self.routes
            print "Configured routes: %d" % len(self.routes)


    def __iter__(self):
        return iter(self.routes)

    def __next__(self):
        for item in self.routes:
            yield (item)

# default patterns for backward compatibility
# patterns = RegexURLMap()
