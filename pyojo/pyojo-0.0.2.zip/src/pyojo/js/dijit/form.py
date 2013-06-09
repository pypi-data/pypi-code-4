# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------

from pyojo.js.code import Code
from pyojo.js.dojo._base import Dojo
from . import Dijit

class Button(Dijit):
    """ 
        @param label: Label
        @param onClick: function
    
    """
    startup = False
    require = ["dojo/ready","dijit/form/Button"]

    
class SimpleTextarea(Dojo):
    require = ["dojo/ready", "dijit/form/SimpleTextarea"]
    
    def __init__(self, name, target): 
        
        self.loc = "var %s = new SimpleTextarea({rows:4}, '%s');" % (name, 
                                                                     target)
        
sss = """[      { label: "Español", value: "ES", selected: true },
                { label: "Inglés", value: "EN" },
                { label: "Alemán", value: "GR" },
                { label: "Francés", value: "FR" },
                { label: "Chino", value: "CH" }
      ]"""
                
class Select(Dijit):
    require = ["dojo/ready","dijit/form/Select"]

    
    def init(self):
        self.para.update({"name":self.name, "options":Code(sss)})