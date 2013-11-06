#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009-2012 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved.
# <LICENSE=ISC>
#
import sys
import traceback

from django.template        import RequestContext 
#from notmm.utils.http       import last_modified
from notmm.utils.wsgilib    import (
    HTTPNotModifiedResponse, 
    HTTPResponse, 
    HTTPServerError
    )
from .configuration         import get_template_loader, get_app_conf, TemplateException
from datetime               import datetime
from time                   import ctime

TemplateLoader = get_template_loader()

__all__ = ['direct_to_template']
def render_template(template_name, ctx, charset='utf-8', disable_unicode=False):

    try:
        t = TemplateLoader.get_template(template_name)
        if charset == 'utf-8' and not disable_unicode:
            setattr(t, 'output_encoding', charset)
            chunk = t.render_unicode(data=ctx)
        else:
            chunk = t.render(data=ctx)
    except TemplateException as e:
        # Template error processing a unicode template
        # with Mako
        exc_type, exc_value, exc_tb = sys.exc_info()
        
        rawtb = ''.join([item for item in traceback.format_tb(exc_tb)])
        
        raise HTTPServerError(
            'error processing template: %s'
            '\n'
            '%r'
            '\n'
            '%s' % (template_name, repr(e), rawtb))
    return t, chunk

def direct_to_template(request, template_name, extra_context={}, 
    status=999, charset='UTF-8', mimetype='text/html', 
    disable_unicode=False):
    """
    Generic view for returning a Mako template inside a simple 
    ``HTTPResponse`` instance. 
    
    """
    #assert 'get_and_delete_messages' in request.__dict__

    # Make sure ctx has our stuff
    if not isinstance(extra_context, RequestContext):
        ctx = RequestContext(request, extra_context)
    else:
        ctx = extra_context

    t, chunk = render_template(template_name, ctx)
    
    # Generate the etag for this template
    #etag = last_modified(t.last_modified)
    httpheaders = (
        ('Last-Modified', datetime.fromtimestamp(t.last_modified).ctime()), 
        ('Date', ctime()))
    if status < 999:
        real_status = status
    else:
        real_status = 200 #500 #server error
    return HTTPResponse(chunk, status=real_status, headers=httpheaders, mimetype=mimetype)

