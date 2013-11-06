#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) Etienne Robillard 2007-2010 <erob@gthcfoundation.org>
# All rights reserved.
# 
from notmm.utils.wsgi import HTTPRedirectResponse
from wsgiapp.views import render_to_response

__all__ = ['handle302', 'handle404', 'handle500']

def handle302(request, **kwargs):
    location = kwargs['location']
    return HTTPRedirectResponse(location=location)

def handle500(request, **kwargs):
    template_name = '500.mako'
    return render_to_response(request, template_name)
 
def handle404(request, **kwargs):
    template_name = '404.mako'
    return render_to_response(request, template_name, \
        status_code=404)
    
