# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------


from pyojo.all import *


def define_run(code):
    return """
define(["pyojo/js/xml","dojo/domReady!"], 
  function(xml){
    return {
      run: function(){
      %s
      }
    };
});""" % code


def _menu():
    return (dijit.DropDownMenuItem("Menu_debug", "Desarrollo", "Menu_tools", iconClass="pyojoIconAccept"),#iconClass=ICON["Connector"]),
            dijit.MenuItem("Menu_debug", "Explorador", id="menu_dev_file", iconClass=ICON["Closed"]),
            dijit.MenuItem("Menu_debug", "Configuración", id="menu_dev_cfg", iconClass=ICON["Configure"]),
            dijit.MenuItem("Menu_debug", "Sesión", id="menu_dev_session", iconClass=ICON["Leaf"]),
            dijit.MenuItem("Menu_debug", "Errores", id="menu_dev_err", iconClass=ICON["Error"]),
            dojo.on("menu_dev_file", "click", js.recall("dev/server/files")),
            dojo.on("menu_dev_cfg", "click", js.recall("dev/server/config")),
            dojo.on("menu_dev_session", "click", js.recall("dev/server/session")),
            dojo.on("menu_dev_err", "click", js.recall("dev/server/err")), 
           ) 

def _dev():
    return ( layout.ContentPane("dev", title="Desarrollo", content ="<button id=\"b1\"></button>").add("TABS"),
             form.Button(label = 'Aceptar', node='b1', iconClass="pyojoIconAccept")
             )
# ----------------------------------------------------------------------------

def main():
    
    code =  js.Require(
                      _menu(), 
                      _dev(),
                      "status('Debug Interface ready.');"
                      ).code()


    return define_run(code)


