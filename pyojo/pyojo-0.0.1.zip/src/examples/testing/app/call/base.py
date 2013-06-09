# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
""" Sends initial page layout.

Calls gui.run()

"""


from pyojo.all import *



def _menu():
    m = js.dijit.MenuBar("Menu", "MENUBAR")
    m.menu("Menu_sys", "Sistema")
    m.menu("Menu_edit", "Editar")
    m.menu("Menu_tools", "Herramientas")
    m.menu("Menu_help", "Ayuda")
    
    m.item("Menu_sys", "Acceso", id="menu_login", iconClass=ICON["Key"])
    m.item("Menu_sys", "Salir", id="menu_exit", iconClass=ICON["Delete"])
    
    m.item("Menu_edit", "Cortar", iconClass=ICON_EDIT["Cut"])
    m.item("Menu_edit", "Copiar", iconClass=ICON_EDIT["Copy"])
    m.item("Menu_edit", "Pegar", iconClass=ICON_EDIT["Paste"])
    #m.submenu("Menu_info", "Información", sub="Menu_tools")
    return m


def _events():
    return (dojo.on("TREE", "click", "status('Sidebar Event')"), 
            dojo.on("LINK", "click", "status('Sidebar Event2')"), 
            dojo.on("menu_exit", "click", "alert('Exit')")
           ) 
     

def _layout():
    
    p = js.DOM("base").add("PANEL", layout.BorderContainer)
    p.add("MENUBAR", region="top")

    p.add("MAIN", region="center")
    p["MAIN"].add("TABS", layout.TabContainer)
    p["TABS"].add("VIEW", title="Vista")
    p["TABS"].add("INFO", title="Información")

    p.add("SIDE", region="leading", splitter=True, 
          style="padding:0px; margin:0px; width:200px")
    p["SIDE"].add("ROWS", layout.AccordionContainer)
    p["ROWS"].add("TREE", title="Explorador")
    p["ROWS"].add("LINK", title="Accesos")
    
    p.add("DOWN", region="bottom", splitter=True,
          style="padding:0px; margin:0px; height:0px;")

    p.add("status", region="bottom", splitter=True,
          content="Loading...",
          style="background-color:rgb(239, 239, 239); overflow:hidden;")
    
    
    log = dojo.domConstruct("textarea", "log", "DOWN")
    msg = "log('%s');" % ("Server python "+sys.version.replace("\n", " ")) 

    return p.blocks() + [ _menu(), 
                      _events(), log, msg, 
                      js.Code("PANEL.resize();") ]
                       


    

def main():
    me = js.Dojo().requires("pyojo/gui", "dojo/domReady!")
    me.js="gui.run()" 
    return js.Require(_layout(), 
                      "status('Base layout created.');",
                      me, 
                      )




