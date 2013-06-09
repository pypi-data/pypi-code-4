# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
import pyojo
from pyojo import server


@pyojo.route("/")
def RoutesPage(request):
    a = pyojo.ScriptXML()
    a.call("dev/gui")
    a.code("var a=1;")
    a.script("/static/js/alert.js")
    a.content("info", u"Información")    
    a.new_node("custom", {"style":"bold"})
    
    return a

server.main()
