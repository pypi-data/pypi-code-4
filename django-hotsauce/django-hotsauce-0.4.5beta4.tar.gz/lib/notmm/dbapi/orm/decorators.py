#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2011 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# <LICENSE=ISC>
"""Decorator functions to interact with Schevo databases"""

from functools import wraps
from notmm.controllers.schevo import SchevoController
from notmm.utils.wsgilib import HTTPRequest

__all__ = ('with_schevo_database',)


def with_schevo_database(dbname='test', request_class=HTTPRequest):
    """
    Decorator that adds a schevo database object reference
    in the ``request.environ`` dictionary.

    """


    def decorator(view_func, **kwargs):
        def _wrapper(*args, **kwargs):
            
            if not isinstance(args[0], request_class):
                req = request_class(environ=args[0])
            else:
                req = args[0]
            #assert isinstance(dbname, str), 'dbname should be a string, bummer!'
            wsgi_app = SchevoController(req, dbname)
            wsgi_app.process_request(req)
            req.db = wsgi_app.db
            return view_func(req, **kwargs)
        #locals()['dbname'] = dbname    
        #print "dbname: %s" % dbname
        return wraps(view_func)(_wrapper, **kwargs)
    return decorator

