# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Base classes for dijit objects.
"""

from pyojo.func import Error
from pyojo.js.code import js_code, js_check, Object, Code
from pyojo.js.dojo._base import Dojo



class Dijit(Dojo):
    """ Base class for all Dijit widgets.
    """
    require = ["dojo/ready"]
    local = False
    registered = False
    startup = True
    loc_pre = ""
    loc = ""
    loc_post = ""

            
    def __init__(self, name=None, target=None, registered=True, **member):
        if name is not None:
            if type(name)!=type(""):
                raise Error("Object name must be a string.")
        self.name = name
        self.target = target
        self.member = {}
        if registered and name is not None:
            self.member["id"] = name
        self.member.update(member)
        self.init()
    
    def init(self): pass
    
    def place(self, target):
        self.target = target


    def new(self, declare=True):
        """ Get the JavaScript constructor code.
        
            ID is a special member passed as the last parameter.
        """
        ID = self.member.get("ID")
        if ID is None: par = ""
        else: 
            del self.member["ID"]
            par=", '%s'" % ID 
        
        new = "new %s(%s%s)" % (self.__class__.__name__, 
                                     js_code(self.member), par)
        if not declare:
            return new
        loc = "var " if self.local else ""
        var = "" if self.name is None else loc + "%s = " % self.name
        return var + new + ";"


    def code(self, catch=False, start=True, place=None):
        loc = self.loc_pre
        loc += self.new()
        loc += self.loc    
        loc += self.loc_post
        if self.target is not None: 
            loc += "%s.placeAt('%s');" % (self.name, self.target)
        if self.startup: loc += "%s.startup();" % (self.name) 
        
        if self.registered:
            return js_check(self.name, loc)
        else: return loc
    
    def __repr__(self):
        return "<Dijit %s '%s' %s>" % (self.__class__.__name__, 
                                       self.name, self.member)
      
    def set(self, attr, value):
        return Code("%s.set('%s', '%s');" % (self.name, attr, value))

    def resize(self):
        return Code("%s.resize();" % self.name)
        
    def show(self):
        return Code("%s.show();" % self.name)
    
    def hide(self):
        return Code("%s.hide();" % self.name)
    
    

    
    def connect(self, **events):
        """ Allows one function to be called when any other is called.
        
        :param event: the name of the method/event to be listened for.
        """ 
        loc = ""
        for event, func in events.iteritems():
            loc += "%s.connect(%s, '%s', %s);" % (self.name, 
                                                  self.name, event, func)
        #context, method, dontFix
        return self.add_loc(loc)
    
class Registry(Dojo):
    """ Stores a collection of all the dijit widgets within a page.
    
    """
    require = ["dojo/ready", "dijit/registry"]
    

    @staticmethod
    def byId(name):
        """ Retrieve a widget from the registry using a widget ID.
        """
        return Registry("registry.byId('%s');" % (name))

    @staticmethod
    def byNode(domNode):
        """ Retrieve a widget from the registry using its DOM node
        """
        return Registry("registry.byId('%s');" % (domNode))

    @staticmethod
    def getEnclosingWidget(domNode):
        """ Find the nearest enclosing widget for a DOM node
        """
        return Registry("registry.getEnclosingWidget('%s');" % (domNode))
  
    @staticmethod
    def toArray():
        """ Get an Array to iterate over the entire registry.
        """
        return Registry("registry.toArray();")


class WidgetSet(Dojo, Object):
    """ A collection of Dijit widgets.
    """
    require = ["dojo/ready", "dijit/WidgetSet"]

# ----------------------------------------------------------------------------
