# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
""" Common methods..  
"""

from pyojo.js.code import js_code




class ArrayMixin(object):
    
    @classmethod
    def forEach(cls, arrayObject, callback, fromIndex=0):
        """ Iterate over arrays.
        """
        para = "%s, %s" % (js_code(arrayObject), callback)
        if fromIndex!=0: 
            para +=", %s" % fromIndex
        return cls("%s.forEach(%s)" % (cls.__name__, para))

    @classmethod
    def indexOf(cls, arrayObject, valueToFind, fromIndex, findLast):
        """ Determine the index of an element in an array, or -1 if not found.
        """
        pass

    @classmethod
    def lastIndexOf(cls, arrayObject, valueToFind, fromIndex):
        """ Determine the the last index of an element in an array.
        """
        pass

   

    @classmethod
    def filter(cls, unfilteredArray, callback):
        """ Filters an array by a certain condition.
        """
        return cls("%s.filter(%s, %s)" % (cls.__name__, unfilteredArray, callback))

    @classmethod
    def map(cls, arrayObject, callback):
        """ Run a function on all elements of an array.
        
        :returns: a new array with the changed values.
        """
        pass

    @classmethod
    def some(cls, arrayObject, callback):
        """ Run a function on all elements and check if any returns true.
        
        :returns: true if any item returns true.
        """
        return cls("%s.some(%s, %s)" % (cls.__name__, arrayObject, callback))
    

    @classmethod
    def every(cls, arrayObject, callback, thisObject):
        """ Run a function on all elements and check if all return true.
        
        :returns: true if all items returns true.
        """
        return cls("%s.every(%s, %s)" % (cls.__name__, arrayObject, callback))
        



    
class NodeListMixin(ArrayMixin):

    def on(self, event, func): 
        """ Add event handlers to all DOM Nodes in the list. 
        
        :param function: a Javascript function.
        """
        self.chain +=".on('%s', %s)" % (event, js_code(func))
        return self
    

    def val(self, value=None):
        """ If a value is passed, allows seting the value property of form elements in this
        NodeList, or properly selecting/checking the right value for radio/checkbox/select
        elements. If no value is passed, the value of the first node in this NodeList
        is returned.
        """
        pass
    
    def toString(self):
        """ 
        """
        pass
        
    def innerHTML(self, value):
        """ allows setting the innerHTML of each node in the NodeList,
        """
        pass
    
    def text(self, value):
        """ allows setting the text value of each node in the NodeList,
        """
        pass
    
    
    def anim(self, properties, duration, easing, onEnd, delay):
        """ Animate one or more CSS properties for all nodes in this list.
        """
        pass

    def closest(self, query, root):
        """ Returns closest parent that matches query, including current node in this
        dojo.NodeList if it matches the query.
        """
        pass
    
    def connect(self, methodName, objOrFunc, funcName):
        """ Attach event handlers to every item of the NodeList. Uses dojo.connect()
        so event properties are normalized.
        """
        pass
    
    def data(self, key, value):
        """ stash or get some arbitrary data on/from these nodes.
        """
    
    def delegate(self, selector, eventName, fn):
        """ Monitor nodes in this NodeList for [bubbled] events on nodes that match selector.
        Calls fn(evt) for those events, where (inside of fn()), this == the node
        that matches the selector.
        """
        pass

    def filter(self, filter):
        """ &quot;masks&quot; the built-in javascript filter() method (supported
        """
        pass
    
    def html(self, content, params):
        """ see the information for innerHTML.
        """
        pass
    
    def indexOf(self, value, fromIndex=0):
        """ see dojo.indexOf(). The primary difference is that the acted-on
        """
        pass
    
    def lastIndexOf(self, value, fromIndex=0):
        """ see dojo.lastIndexOf(). The primary difference is that the
        acted-on array is implicitly this NodeList
        """
        pass
    
    def instantiate(self, declaredClass, properties):
        """ Create a new instance of a specified class, using the
        specified properties and each node in the nodeList as a
        srcNodeRef.
        """
        pass
    
    
    def remove(self, simpleFilter):
        """ alias for dojo.NodeList's orphan method. Removes elements
        """
        pass
    
    def removeData(self, key):
        """ Remove the data associated with these nodes.
        """
        pass
    
    def slice(self, begin, end):
        """ Returns a new NodeList, maintaining this one in place
        """
        pass
    
    def splice(self, index, howmany, item):
        """ Returns a new NodeList, manipulating this NodeList based on
        the arguments passed, potentially splicing in new elements
        at an offset, optionally deleting elements
        """
        pass
    
    def wrap(self, html):
        """ Wrap each node in the NodeList with html passed to wrap.
        """
        pass
        
    def wrapAll(self, html):
        """ Insert html where the first node in this NodeList lives, then place all
        nodes in this NodeList as the child of the html.
        """
        pass
    
    def wrapInner(self, html):
        """ For each node in the NodeList, wrap all its children with the passed in html.
        """
        pass
    
    


def __add_chain_func_method(cls, name, doc=""):
    
    def method(self, func):
        self.chain +=".%s(%s)" % (name, js_code(func))
        return self
    
    method.__name__ = name
    method.__doc__ = doc+"\n\n:param function: a Javascript function."
    setattr(cls, name, method)

__NodeList_dom_events = {
    "onclick": "The user clicked a node.",
    "onfocus": "A node received focus.",
    "onblur": "A node was ‘blurred’, or otherwise lost focus.",
    "onchange": "An input value was changed.",
    "onkeypress": "Fired when the user presses a key.",
    "onkeydown": "Shouldn’t be necessary, all key presses go to onkeypress.",
    "onkeyup": "Fired when the user releases a key.",
    "onmouseover": "A node was hovered.",
    "onmouseout": "A node was un-hovered.",
    "onmouseenter": "A normalized version of onmouseover.",
    "onmouseleave": "A normalized version of onmouseout.",
    "onsubmit": "A form has been submitted",
    "onload": "Fired upon load",
    "onerror": "A error ocurred."}

for method, doc in __NodeList_dom_events.iteritems():
    __add_chain_func_method(NodeListMixin, method, doc)


__NodeList_func = {
    "every": "",
    "forEach": "Runs a function for each element in a NodeList",
    "map": "",
    "some": ""}

for method, doc in __NodeList_func.iteritems():
    __add_chain_func_method(NodeListMixin, method, doc)

#classmethods returning new query
__NodeList_NodeList = {
    "andSelf": "Adds the nodes from the previous NodeList to the current NodeList.",
    "clone": "Clones all the nodes in this NodeList and returns them as a new NodeList.",
    "end": "Ends use of the current `dojo.NodeList` by returning the previous dojo.NodeList.",
    "even": "Returns the even nodes in this dojo.NodeList as a dojo.NodeList.",
    "first": "Returns the first node in this dojo.NodeList as a dojo.NodeList.",
    "last": "Returns the last node in this dojo.NodeList as a dojo.NodeList.",
    "odd": "eturns the odd nodes in this dojo.NodeList as a dojo.NodeList."}


# add js line
__NodeList_obj = {
    "animateProperty": "nimate all elements of this NodeList across the properties specified.",
    "fadeIn": "Fade in all elements of this NodeList.",
    "fadeOut": "Fade out all elements of this NodeList.",
    "slideTo": "Slide all elements of the node list to the specified place.",
    "wipeIn": "Wipe in all elements of this NodeList.",
    "wipeOut": "Wipe out all elements of this NodeList."}


__NodeList_query = {
    "appendTo": "Appends nodes in this NodeList to the nodes matched by the query.",
    "children": "Returns all immediate child elements for nodes in this NodeList",
    "insertAfter": "The nodes in this NodeList will be placed after the nodes matched by the query.",
    "insertBefore": "The nodes in this NodeList will be placed before the nodes matched by the query.",
    "prependTo": "Prepends nodes in this NodeList to the nodes matched by the query.",
    "replaceAll": "Replaces nodes matched by the query passed to replaceAll with the nodes."}

#chain?
__NodeList_query_opt = {
    "next": "Returns the next element for nodes in this dojo.NodeList.",
    "nextAll": "Returns all sibling elements that come after the nodes in this dojo.NodeList.",
    "parent": "Returns immediate parent elements for nodes in this dojo.NodeList.",
    "parents": "Returns all parent elements for nodes in this dojo.NodeList.",
    "prev": "Returns the previous element for nodes in this dojo.NodeList.",
    "prevAll": "Returns all sibling elements that come before the nodes in this dojo.NodeList.",
    "siblings": "Returns all sibling elements for nodes in this dojo.NodeList."}

__NodeList_content = {
    "after": "Places the content after every node in the NodeList.",
    "append": "Appends the content to every node in the NodeList.",
    "before": "Places the content before every node in the NodeList.",
    "prepend": "Prepends the content to every node in the NodeList.",
    "replaceWith": "Replaces each node in ths NodeList with the content."}

    
