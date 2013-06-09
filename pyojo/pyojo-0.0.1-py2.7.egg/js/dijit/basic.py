# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Dojo Dijit widget collection.
"""

from . import Dijit
from pyojo.js.code import js_code, Code
from pyojo.js.dojo._base import Dojo



class Tooltip(Dijit):
    """ Create a Tooltip
       
        :param connectId:
            An array of IDs or DOM nodes that the Tooltip should be 
            connected to.
        :param label:
            The HTML or text content to be placed within the Tooltip
        :param showDelay: 
            The show delay of the Tooltip

    """
    require = ["dojo/ready","dijit/Tooltip"]


class Dialog(Dijit):
    """ Create a Dialog.
           
        :param title:
            The title to display atop the Dialog
        :param content: 
            The HTML or text content for the Dialog
        :param draggable:
            Represents if the Dialog should be draggable
        :param href: 
            If content is to be loaded by Ajax (xhrGet), a path to that 
            content file
        :param loadingMessage:
            Message to be shown while the Ajax content is loading.
        :param open:
            Returns true if the Dialog instance is presently open

    """
    require = ["dojo/ready","dijit/Dialog"]



# ----------------------------------------------------------------------------


class Tree(Dijit):
    require = ["dojo/ready","dijit/Tree"]
    
    def store(self, store, root="root"):
        self.require.append("dijit/tree/ObjectStoreModel")    
        para = "{store: %s, query: {id: '%s'}}" %(store, root)
        model = Code("new ObjectStoreModel(%s)" % (para))
        self.para.update({'model': model})



#-----------------------------------------------------------------------------
#--- MENU

class MenuItem(Dojo):
    require = ["dojo/ready", "dijit/MenuItem"]
            
    def __init__(self, menu, label, **member):
        self.menu = menu
        self.member = {"label": label}
        self.member.update(member)
    
    def code(self):
        return "%s.addChild(new MenuItem(%s));" % (self.menu, 
                                                   js_code(self.member))


class DropDownMenu(Dojo):
    require = ["dojo/ready",
               "dijit/DropDownMenu", 
               "dijit/PopupMenuBarItem"]
            
    def __init__(self, name, label, target, **member):
        self.name = name
        self.target = target
        
        self.member = {"label": label, 'popup': Code(name)}
        self.member.update(member)
        
    def code(self):        
        loc = "%s = new DropDownMenu({});" % self.name
        loc += "%s.addChild(new PopupMenuBarItem(%s));" % (self.target, 
                                                         js_code(self.member))
        return loc



class DropDownMenuItem(Dojo):
    require = ["dojo/ready",
               "dijit/DropDownMenu", 
               "dijit/PopupMenuItem"]
            
    def __init__(self, name, label, target, **member):
        self.name = name
        self.target = target
        self.member = {"label": label, 'popup': Code(name)}
        self.member.update(member)
    
    def code(self):
        loc = "%s = new DropDownMenu({});" % self.name
        loc += "%s.addChild(new PopupMenuItem(%s));" % (self.target, 
                                                     js_code(self.member))
        return loc



class MenuBar(Dijit):
    """MenuSeparator
    """
    require = ["dojo/ready",
               "dijit/MenuBar", 
               "dijit/PopupMenuBarItem", 
               "dijit/Menu", 
               "dijit/MenuItem", 
               "dijit/PopupMenuItem", 
               "dijit/DropDownMenu"]
    
    def menu(self, name, label, **kwargs):
        """ Add a DropDownMenu.
        """
        self.loc += DropDownMenu(name, label, self.name, **kwargs).code()
      
    def submenu(self, name, label, sub, **kwargs):
        """ Add a DropDownMenuItem.
        """
        self.loc += DropDownMenuItem(name, label, sub, **kwargs).code()
        
    def item(self, menu, label, **kwargs):
        """ Add a MenuItem.
        """
        self.loc += MenuItem(menu, label, **kwargs).code()
        
        
