# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" This module contains the base classes for the all the javascript 
generation objects.
"""

import re

from pyojo.func import jsbeautify, jsb_opts
from .code import *
from .dojo import Dojo
from .utils import *
from .lib import *

import dojo
from .dojo.modules import Require, Define, call, recall 

import dijit
from .dijit import form

# ----------------------------------------------------------------------------

def get_code(*args):
    """ Get the Javascript code for the argument list.
    
        If any of the blocks has Dojo requires, all the code will be inside a
        require block.
    """
    #require = any(isinstance(a, Dojo) for a in args)
    require = has_require(args)
    if require:
        r = Require(*args)
        r.catch = False
        return r.code()
    loc = ""
    for a in args:
        loc += js_code(a)
        
    return loc



def see(*args):      
    """ Return the generated Javascript for the argument list.
    """
    loc = get_code(*args)
    if jsbeautify is not None:
        return jsbeautify(loc, jsb_opts)
    else:
        return loc


# ----------------------------------------------------------------------------




class Block(Code):
    """ Base class for code blocks.
    """
    def __init__(self, name=None):
        if name is None:
            self.name = "JS%s" % id(self)
            self.catch = False
        else: 
            self.name = name
            self.catch = True
        self.blocks = []

    def __repr__(self):
        return "<Block '%s' (%s)}" % (self.name, len(self.blocks))
         
    def __add__(self, code):
        self.blocks.append(code)
        return self

    def __iter__(self):
        return iter(self.blocks)

    def get_code(self, block):
        """ Appends requirements and returns the code.
        """
        if hasattr(block, "get_requires"):
            new = dojo.Dojo().requires(*block.get_requires())
            self.blocks.append(new)
        return Code(js_code(block))

    def code(self):
        if getattr(self, "catch", False): 
            return js_try(get_code(*self.blocks), self.name)
        else:
            return get_code(*self.blocks)
 


class Alert(Block):
    require=[]
    
    def __init__(self, title, content):
        self.name = "dialog%s" % id(self)
        dialog = dijit.Dialog(self.name, 
                              title=title)
        bid = "btn%s" % id(self)
        button = form.Button(label = 'Aceptar', 
                 ID=bid, 
                 iconClass="pyojoIconAccept", 
                 onClick=Function(dialog.hide().code()))
        
        b = '<div align="right"><button id="%s"></button></div>' % bid
        self.blocks = [dialog, 
                       dialog.set('content', content+b),
                       button,
                       dialog.show()]