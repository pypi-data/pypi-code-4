#!/usr/bin/env python
# Copyright (c) Etienne Robillard 2007-2012
# <LICENSE=ISC>
"""Custom WSGI response handlers for BlogEngine"""

from notmm.utils.wsgilib import HTTPRedirectResponse
from blogengine.template import direct_to_template

__all__ = ('handle302', 'handle404', 'handle500')

def handle302(request, location='/'):
    return HTTPRedirectResponse(location=location)

def handle500(request, **kwargs):
    template_name = kwargs.pop('template_name', '500.mako')
    return direct_to_template(request, template_name, status=500)
 
def handle404(request, **kwargs):
    template_name = kwargs.pop('template_name', '404.mako')
    return direct_to_template(request, template_name, status=404)
    
