# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# pyojo                                            Copyright (c) 2011 nabla.net
#------------------------------------------------------------------------------
""" Event handling.
"""

from _base import Dojo

    
#------------------------------------------------------------------------------
#--- Events

class on(Dojo):
    """ Attach an event.
    """
    require = ["dojo/on", "dojo/dom"]
    
    def __init__(self, target, event="click", code=""):    
        self.function = "function(e){%s}" % code
        self.event = event
        self.target = target
    
    def code(self):        
        return "on(dom.byId('%s'), '%s', %s);" % (self.target, 
                                                  self.event, 
                                                  self.function)


class connect(Dojo):
    """ Connects events to methods. Deprecated, now use dojo/on.
    """
    require = ["dojo/connect"]
    
    @staticmethod
    def connect(obj, event, context=None, method=None, dontFix=None):
        """ Allows one function to be called when any other is called.
        
        :param obj: the DOM node.
        :param event: the name of the method/event to be listened for.
        """ 
        par=""
        #context, method, dontFix
        return connect("connect.connect(%s, '%s'%s);" % (obj, event, par))

    @staticmethod
    def disconnect(link):    
        """ Disconnect a event listener.
        
        :param link: the returned value from a connect.
        """ 
        return connect("connect.disconnect(%s);" % link)
    
class keys(Dojo):
    """  Provides normalized constants for all the available keys you can 
    press.
    """
    require = ["dojo/keys"]

class mouse(Dojo):
    """  Events for hovering and mouse button utility functions.
    """
    require = ["dojo/mouse"]
    
    
class touch(Dojo):
    """ Provides a set of events designed to work similarly on a desktop 
    browser (e.g. with mouse) and touch devices.
    """
    require = ["dojo/touch"]

class robot(Dojo):
    """ Module for simulating user input.
    """
    require = ["dojo/robot"]

class dnd(Dojo):
    """ The drag and drop (DnD) package/system of Dojo.
    """
    require = ["dojo/dnd"]


