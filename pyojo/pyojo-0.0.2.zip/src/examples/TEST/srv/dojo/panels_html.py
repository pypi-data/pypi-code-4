# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------

import pyojo
from pyojo import js
from pyojo.js import dijit


def layout():
    
    b = dijit.layout.BorderContainer("MiPanel", "base")
    b.panel("top", "menubar", content="top")
    b.panel("center", "main", content="center")
    b.panel("leading","sidebar", splitter=True, content="leading",
            style="padding:0px; margin:0px; width:200px")
    b.panel("bottom", "status", content="bottom",
            style="background-color:rgb(239, 239, 239); overflow:hidden;")
    
    acc = dijit.layout.AccordionContainer("accordion", "sidebar")
    for i in range(1,9):
        acc.panel("side%s" % i, "Side %s" % i)

    
    tabs = dijit.layout.TabContainer("tabs", "main")
    for i in range(1,9):
        tabs.panel("tab%s" % i, "Tab %s" % i)

    
        
    return b, tabs, acc, b.resize()


def GET(request):
    
    test = pyojo.TestPage()
    test.script(js.get_code(*layout()))
    return test.html()