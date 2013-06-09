# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
"""Miscellaneous utility objects.
"""

from .dijit.layout import ContentPane


class DOM(object):
    """ A shortcut to declare Dijit trees.
        
        Example:
    
        .. code-block:: python
        
            p = js.DOM("base").add("PANEL", layout.BorderContainer)
            p.add("MENUBAR", region="top")
        
            p.add("MAIN", region="center")
            p["MAIN"].add("TABS", layout.TabContainer)
            p["TABS"].add("VIEW", title="Vista")
            p["TABS"].add("INFO", title="Información")
            js.Require(p.blocks()).code()
    
    """
    
    def __init__(self, name=None, cls=None, **kwargs):
        """ Declare a DOM node.
        
            The keyword arguments will be used to create the class.
            
            :param name: DOM ID
            :param cls: class
            
        """
        self.name = name
        self.cls = cls or ContentPane
        self.prop = kwargs
        self.instance = None
        self.parent = None
        self.children = []

    def __repr__(self):
        return "<%s %s %s>" % (self.__class__.__name__,
                               self.name, self.cls)
        
    def __setitem__(self, key, value):
        value.name = key
        self.children.append(value)

    def __getitem__(self, key):
        for obj in self.family():
            if obj.name==key:
                return obj
        return None
        

    def iteritems(self):
        for child in self.children:
            print "Yield %s" % child.name
            yield child
            child.iteritems()
    
    def add(self, name, cls=None, **kwargs):
        new = self.__class__(name, cls, **kwargs)
        new.parent = self
        self.children.append(new)
        return new

    def structure(self):
        s = {}
        for child in self.children:
            s.update(child.structure())
        return {self.name:s}
            
    def family(self):
        children = []
        for child in self.children:
            children.append(child)
            children += child.family()
        return children

    def names(self):
        return [child.name for child in self.family()]
    
    def get_element(self, name):
        if name==self.name: return self
        for child in self.children:
            if child.get_element(name) is not None:
                return child
        return None       

    def info(self):
        x=[]
        for node in self.family():
            x += ["Node %s" % node,
                 "    Name: %s " % node.name,
                 "    Type: %s " % node.cls,
                 "    Prop: %s " % node.prop]
        return '\n'.join(x)

    def code(self, catch=False):
        if self.cls is None:
            return ""
        self.prop["name"]=self.name
        self.prop["target"]=self.parent.name
        #prop["registered"]=True
        if hasattr(self.parent.cls, "panel"):
            self.instance = self.parent.cls.panel(self.parent.instance,
                                                  **self.prop)
        else:
            self.instance = self.cls(**self.prop)
        return self.instance


    def blocks(self):
        code = [self.code()]
        for child in self.children:
            code +=child.blocks()
        return code
    
    
