#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""BaseController API 1.0

This package provides the ``BaseController`` class
to define custom WSGI middlewares and applications.

See the documentation online at

    http://gthcfoundation.org/documentation/notmm/reference/basecontroller-api.html

Copyright (C) 2010 Etienne Robillard erob@gthcfoundation.org
All rights reserved
"""

#from notmm.controllers.wsgi    import WSGIController, process_exception
#from notmm.controllers.session import SessionController
#from notmm.controllers.routing import (
#    RegexURLMap, url, include, patterns
#    ) 

__all__ = [
    'auth', 
    'django_base', 
    'elixir', 
    'schevo', 
    'session', 
    'wsgi', 
    'i18n'
    ]

