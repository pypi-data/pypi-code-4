# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
import re
import pyojo
from pyojo import js




def GET(request):
    
    text = pyojo.http_request_headers(request.environ)
    
    pre = pyojo.pretty(text).replace("'", '"').replace("\n", "\\n")
    content = "<p>Environ</p><pre>%s</pre>" % pre
    
    
    dialog = js.Alert("Test Alert", content)
    
    
    test = pyojo.util.TestPage()
    test.script(dialog.code())
    return test.html()

