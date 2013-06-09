# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Document Object Model manipulation.  
"""

from pyojo.js.code import js_code, Code
from _base import Dojo 
from mixins import ArrayMixin, NodeListMixin


class domReady(Dojo):
    """ AMD loaded plugin that will wait until the DOM has finished loading 
    before returning
    """
    require = ["dojo/domReady!"]

class ready(Dojo):
    """ registers a function to run when the DOM is ready and all outstanding 
    require() calls have been resolved, and other registered functions with a 
    higher priority have completed.
    """
    require = ["dojo/ready"]


class html(Dojo):
    """ Provides useful utilities for managing HTML.
    """
    require = ["dojo/html"] 
    
    @staticmethod
    def set(node, cont, params=None):
        """ Replace an element’s content.
        
        Provides some hooks and options for how the replacement should be 
        handled.
        
        :param node: DOM node.
        :param cont:
            The content that should be set, which can be a string a DOM node, 
            a NodeList or any other enumerable list of nodes.
        :param params: 
            Optional a hash of options/flags that affect the behavior.
        
        Options:
        
         - *cleanContent*: Should the content be treated be stripped of 
           <!DOCTYPE> and other content that might be an issue (false). 
         - *extractContent*: Real content be stripped out of the <html> and 
           <body> tags before injection (false).
         - *parseContent*: Use dojo/parser before being set in order to 
           instantiate any marked up Objects (false).
         - *parserScope*: String passed to the parser to identify the “scope” 
           of which to identify the marked up content. 
         - *startup*: Start the child widgets after parsing content (true). 
         - *onBegin*: Function called right before the content is replaced. 
           Call this.inherited(arguments) in your custom function.
         - *onEnd*: Function called right after the content is replaced. Call 
           this.inherited(arguments) in your custom function.
         - *onContentError*: Function called whenever there is an error 
           replacing the content.
        
        """
        params = params or {}
        return html("html.set(%s, '%s', %s);" % (node, cont, js_code(params)))    



class NodeList(Dojo):
    """ Standard Arrays, decorated with many helpful functions.
    
    The helper functions attached to the NodeList typically return the same 
    instance of the NodeList, allowing you to call several methods in a row.
    """
    require = ["dojo/NodeList-dom"] #FIX No argument! 
    
    
    
class query(Dojo, NodeListMixin):
    """ Provides useful utilities for managing HTML as NodeLists.
    
    :param query: search string.
    :returns: instance of dojo.NodeList
    """
    require = ["dojo/query"]
    
    def __init__(self, query):
        self.query = query
        self.loc = ""
        self.chain = ""
        
    def set(self): pass


    def code(self):
        self.loc = 'query("%s")%s;' % (self.query, self.chain)
        return super(query, self).code()



class parser(Dojo):
    """ Browser feature detection.
    """
    require = ["dojo/parser"]
    
class uacss(Dojo):
    """ Adds browser “centric” CSS classes to a the document’s <html> tag.
    """
    require = ["dojo/uacss"]

class fx(Dojo):
    """ Special effects.
    """
    require = ["dojo/fx"]


#------------------------------------------------------------------------------
#--- DOM
    


class dom(Dojo):
    """ This module defines the core Dojo DOM API.
    """
    require = ["dojo/dom"]
    
    @staticmethod
    def byId(name):
        return dom("dom.byId('%s');" % (name))
        
    def isDescendant(self): pass
    def setSelectable(self): pass
    
    

class domAttr(Dojo):
    """ A unified API to deal with DOM node attribute and property values.
    
     It checks an attribute and if there is a property with the same name, it 
     will get/set its value. Otherwise it will work with DOM node attributes.
    
    """
    require = ["dojo/dom-attr"]
    
    @staticmethod
    def get(node, attr):
        """ Return attribute value, or false.
        
        :param node: id or reference of the DOM node.
        :param attr: the attribute property name.
        """ 
        return domAttr("domAttr.get(%s, '%s');" % (node, attr))

    @staticmethod
    def set(node, attr, value=None):
        """ Return attribute value, or false.
        
        :param node: id or reference of the DOM node.
        :param attr: the attribute property name, or many {"name":value}
        :param value: the value for the attribute.
        
        """ 
        if value is None:
            return domAttr("domAttr.set(%s, %s);" % (node, 
                                                     js_code(attr)))
        return domAttr("domAttr.set(%s, %s, %s);" % (node, 
                                                     js_code(attr), 
                                                     js_code(value)))
        
            
    def has(self): pass
    def remove(self): pass
    def getNodeProp(self): pass

 
class domClass(Dojo):
    """ This module defines the core Dojo DOM API.
    """
    require = ["dojo/dom-class"]
        
    def contains(self): pass
    def add(self): pass
    def remove(self): pass
    def replace(self): pass
    def toggle(self): pass
    
     

class domConstruct(Dojo):
    """ Defines the core dojo DOM construction API.
    """
    require = ["dojo/dom-construct", 
               "dojo/domReady!"]
    
    @staticmethod
    def toDom(frag, doc=None): 
        """ Instantiates an HTML fragment returning the corresponding DOM.
        
        :param frag: The fragment of HTML to be converted into a node.
        :param doc: An optional document to use.
        """
        new = domConstruct()
        new.loc = "domConstruct.toDom(%s);" % (frag)
        return new
    
    @staticmethod    
    def place(node, refNode, pos="last"):
        """ A DOM node placement utility function.
        
        :param node: HTML fragment or DOM node.
        :param refNode: The DOM node where the node should be placed.
        :param pos: 
            Position of the new node can be “before”, “after”, “replace”, 
            “only”, “first”, or “last” (default). Or a number.
        
        """
        new = domConstruct()
        new.loc = "domConstruct.place(%s, %s, %s);" % (node, refNode, pos)
        return new

    
    @staticmethod
    def create(tag, refNode, pos="last", **attrs):
        """ A convenient DOM creation, manipulation and placement utility 
        shorthand.
        
        :param tag: Tag of the new DOM node.
        :param refNode: The DOM node where the new node should be placed.
        :param pos: Position of the new node.
        """
        
        para = {"style": Code('{width: "100%", height: "100%"}')}
        para.update(attrs)
        args = "'%s', %s, dom.byId('%s'), '%s'"  % (tag, 
                                                    js_code(para), 
                                                    refNode, pos)
        new = domConstruct().requires("dojo/dom")
        new.loc = "domConstruct.create(%s);" % (args)
        return new
        
    @staticmethod    
    def empty(node): 
        """ Deletes all children but keeps the node there.
        
        :param node: the DOM node.
        """
        new = domConstruct()
        new.loc = "domConstruct.empty(%s, %s, %s);" % (node)
        return new
    
    @staticmethod
    def destroy(node):
        """ Deletes all children and the node itself.
        
        :param node: the DOM node.
        """
        new = domConstruct()
        new.loc = "domConstruct.destroy(%s, %s, %s);" % (node)
        return new    
        

class domForm(Dojo): pass
class domGeometry(Dojo): pass
class domProp(Dojo): pass
class domStyle(Dojo): 
    """ A getter/setter for styles on a DOM node.

    """
    
    @staticmethod
    def get(node, style):
        """ Return style value.
        
        :param node: id or reference of the DOM node.
        :param style: the style property to get in DOM-accessor format.
        """ 
        return domStyle("domStyle.get(%s, '%s');" % (node, style))

    @staticmethod
    def set(node, style, value=None):
        """ Return attribute value, or false.
        
        :param node: id or reference of the DOM node.
        :param style: the style property to set in DOM-accessor format,
            or an object with many key/value pairs.
        :param value: If passed, sets value on the node for style.
        
        """ 
        if value is None:
            return domStyle("domStyle.set(%s, %s);" % (node, 
                                                     js_code(style)))
        return domStyle("domStyle.set(%s, %s, %s);" % (node, 
                                                     js_code(style), 
                                                     js_code(value)))


# ----------------------------------------------------------------------------
 
 

