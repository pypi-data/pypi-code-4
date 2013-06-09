# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
""" Functionality that formally was contained in the base dojo/dojo module.

The dojo/_base directory contains modules with basic functionality, such as 
array operations. Typically, if a function or class exists within the dojo 
namespace directly (e.g. dojo.forEach()) then it is defined in dojo/_base

The dojo/_base files will be maintained until the 2.0 release.

"""

from pyojo.js.code import Code
from mixins import ArrayMixin

class Dojo(Code):
    """ Base class for Dojo javascript parts.
    
        The require list allows to Require and Define to know what to ask to
        the AMD loader. 
    """
    loc = ""
    function = ""
    require = []  # __init__
    
    def requires(self, *args):
        """ Require this AMD module too.
        """
        if getattr(self, "_require", None) is None:
            self._require = []
        for module in args:
            self._require.append(module)
        return self

    def get_requires(self):
        return self.require+getattr(self, "_require", [])
   

#------------------------------------------------------------------------------
#--- Foundation

class kernel(object):
    """ The bootstrap kernel that generates the dojo namespace.
    """
    pass


class config(object):
    """ Configures Dojo and loads the default platform configuration.
    
    To override certain global settings that control how the framework 
    operates.
    """
    pass


class loader(object):
    """ The legacy and AMD module loader for Dojo.
    """
    pass


class lang(Dojo):
    """ Contains functions for supporting Polymorphism and other language 
    constructs that are fundemental to the rest of the toolkit.
    """
    require = ["dojo/_base/lang"]

    
class declare(Dojo):
    """ JavaScript uses prototype-based inheritance, not class-based 
    inheritance (which is used by most programming languages).
    """
    require = ["dojo/_base/declare"]


class array(Dojo, ArrayMixin):
    """ A bunch of useful methods to deal with arrays.
    """
    require = ["dojo/_base/array"]
    


#------------------------------------------------------------------------------
#--- Extras

    
class window(object):
    """Use the window, document, and document.body global variables, 
      or equivalent variables for the frame that you want to operate on.
    """
    pass


class Color(Dojo):
    """ A unified way to store RGBA colors.
    """
    require = ["dojo/_base/Color"]


class fx(Dojo):
    """ The legacy and AMD module loader for Dojo.
    """
    require = ["dojo/_base/fx"]
    
    def animateProperty(self): pass
    def fadeIn(self): pass
    def fadeOut(self): pass
    

class unload(object):
    """ Registers a function to be called when the page unloads.
    """
    def addOnUnload(self): pass
    def addOnWindowUnload(self): pass
    