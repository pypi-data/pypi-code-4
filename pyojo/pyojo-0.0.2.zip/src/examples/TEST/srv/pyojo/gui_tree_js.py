# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
from pyojo import js
from pyojo.func import raw_str
from pyojo.js.lib.tree import TreeJSON
from pyojo.js import dojo 
from pyojo.js import dijit 
        
def GET(request):
    
    tree = TreeJSON("/data/tree.json?item=")
    
    newpanel =  dijit.layout.ContentPane("tab"+str(id(request)),
                                        title=js.Code("item.name"),
                                        registered = False,
                                        extractContent = True,
                                        closable = True,
                                        style = "overflow:auto;",
                                        href = js.Code("item.url + '?code=1'"),
                                        #postCreate = js.Function("sh_highlightDocument();")
                                        #content = js.Code("result")
                                        )
    newpanel.add("TABS")
    newpanel.select("TABS")
    newpanel.connect(onLoad=js.Function("sh_highlightDocument();"))
      
    onload = js.Function('result', 
             [raw_str('log("Received:\n" + result);'),
              'status("Loaded "+item.name + " " + item.ctype+ " ...");',
              "PANEL.resize();"
             ])            
                                
    onclick = js.Function("item", 
              ["status('Loading '+item.name + ' ' + item.ctype+ ' ...');",                  
               newpanel,
               #"TABS.selectChild(%s);" % ("tab"+str(id(request))),
               dojo.request.get(js.Code("item.url + '?code=1'"), 
                                handleAs = js.Code("item.ctype")
                               ).then(onload),
              
              ])
    
    tree.onclick(onclick)
    return tree


