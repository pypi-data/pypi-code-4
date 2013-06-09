# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------

import pyojo
from pyojo import js
from pyojo.js import dojo
from pyojo.js import dijit
from pyojo.js.dijit.icons import ICON, ICON_EDIT



def new_window(url, target="_blank", options="toolbar=0,location=0,menubar=0"):
    return 'window.open("%s", "%s", "%s");' % (url, target, options)


def _icons():
    x=[dijit.DropDownMenuItem("Menu_icon", "Icons", "Menu_tools")]
    icons = ICON.keys()
    icons.sort()
    for icon in icons:
        x.append(dijit.MenuItem("Menu_icon", icon, 
                                id="Menu_icon_"+icon, 
                                iconClass=ICON[icon]))
    return x


def menu():

    m = dijit.MenuBar("Menu", "base")

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
    return [
            dojo.on("menu_exit", "click", "alert('hola');")
           ] 


def GET(request): #_icons(),new_window("http://www.google.es")
    test = pyojo.TestPage()    
    test.script(js.get_code( menu(), *_events()))
    return test.html()