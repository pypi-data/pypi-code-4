# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------

from .. import Object, Dojo


class ObjectStoreModel(Object, Dojo):
    require = ["dijit/tree/ObjectStoreModel"]
    
    def X_new(self):
        if self.name is None: name = ""
        else: name = "var %s = " % self.name        
        self.loc = name + "new %s(%s)" % (self.__class__.__name__, 
                                         self.js_options())
    
    def X__init__(self, name=None, **options):    
        self.name = name
        self.options = options
        self.new()