#!/usr/bin/env python
# -*- encoding: UTF-8 -*-

import os
import helloworld.configuration as c
from notmm.utils.wsgilib import HTTPResponse

def image_handler(request, *args, **kwds):
    # serve a static file using pkg_resources
    docroot = kwds.get('document_root', c.settings.MEDIA_ROOT)
    filename = os.path.split(request.path_url)[-1]
    ext = filename.split('.')[-1]
    content_type = "image/%s" % ext
    
    fdata = file(os.path.join(docroot, filename), 'rb').read()
    headerlist = [
        ('Content-Type', content_type),
        ('Content-Length', str(len(fdata)))
        ]
    response = HTTPResponse(content="%s"%fdata, headerlist=headerlist)
    return response
