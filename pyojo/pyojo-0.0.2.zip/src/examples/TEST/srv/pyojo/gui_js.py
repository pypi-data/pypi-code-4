# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------


from pyojo.all import *




def _menu():
    return (dijit.DropDownMenuItem("Menu_debug", 
                                   "Desarrollo", 
                                   "Menu_tools", 
                                   iconClass="pyojoIconAccept"),#iconClass=ICON["Connector"]),
            dijit.MenuItem("Menu_debug", 
                           "Explorador", 
                           id="menu_dev_file", 
                           iconClass=ICON["Closed"]),
            dijit.MenuItem("Menu_debug", 
                           "Configuración", 
                           id="menu_dev_cfg", 
                           iconClass=ICON["Configure"]),
            dijit.MenuItem("Menu_debug", 
                           "Sesión", 
                           id="menu_dev_session", 
                           iconClass=ICON["Leaf"]),
            dijit.MenuItem("Menu_debug", 
                           "Errores", 
                           id="menu_dev_err", 
                           iconClass=ICON["Error"]),
            
            dojo.on("menu_dev_file", "click", js.recall("data/tree_nav")),
            dojo.on("menu_dev_cfg", "click", js.recall("dev/server/config")),
            dojo.on("menu_dev_session", "click", js.recall("dev/server/session")),
            dojo.on("menu_dev_err", "click", js.recall("dev/server/err")), 
           ) 

def _dev():
    panel = layout.ContentPane("dev", 
                               title="Desarrollo", 
                               content ="<button id=\"b1\"></button>")
    panel.add("TABS")
    return ( panel,
             form.Button(label = 'Aceptar', ID='b1', iconClass="pyojoIconAccept")
             )
# ----------------------------------------------------------------------------

def GET(request):
    code =  js.Require(
                      _menu(), 
                      _dev(),
                      "status('Debug Interface ready.');",
                      
                      ).requires("pyojo/gui_tree")


    #return define_run(code)
    return js.Define(run=code).requires("dojo/domReady!")


