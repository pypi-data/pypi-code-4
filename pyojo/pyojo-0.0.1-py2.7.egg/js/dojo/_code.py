# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
""" Dojo programming utilities.
"""
from pyojo.js.code import js_code
from ._base import Dojo

class Promise(Dojo):
    """ The abstract base class that defines Dojo Promises.
    """
    require = ["dojo/promise/Promise"]
    
    @staticmethod
    def all():
        """ Takes multiple promises and returns a new promise that is fulfilled 
        when all promises have been fulfilled
        """
        require = ["dojo/promise/all"]
    
    @staticmethod
    def first(Dojo):
        """ Takes multiple promises and returns a new promise that is fulfilled 
        when the first of the promises have been fulfilled
        """
        require = ["dojo/promise/all"]
        

    
class when(Dojo):
    """ Transparently applies callbacks to values and/or promises.
    """
    require = ["dojo/when"]

   
#------------------------------------------------------------------------------
#--- Program

class Deferred(Dojo):
    """ Manages the communication between asynchronous threads (callbacks).
    """
    require = ["dojo/Deferred"]


class aspect(Dojo):
    """ Provides aspect oriented programming facilities to attach additional 
    functionality to existing methods.
    """
    require = ["dojo/aspect"]
     

class request(Dojo):
    """ Is a package which provides asynchronous requests.
    
        :param method: HTTP method to use to make the request. 
        :param sync: A boolean that, if true, causes the request to block until 
            the server has responded or the request has timed out.
        :param query: A string or key-value object containing query parameters 
        to append to the URL.
        :param data: A string, key-value object, or FormData object containing 
        data to transfer to the server.
        :param timeout: Time in milliseconds before considering the request a 
        failure and triggering the error handler.
        :param handleAs: A string representing how to convert the text payload 
        of the response before passing the converted data to the success handler. Possible formats are "text" (the default), "json", "javascript", and "xml".
        :param headers: A key-value object containing extra headers to send with 
        the request.
    """
    require = ["dojo/request"]
    
    def __init__(self, url, **params):
        self.url = url   
        self.params = params
        self.loc = "request(%s, %s)" % (js_code(url), js_code(params))

    def then(self, loc):
        self.loc += ".then(%s)" % loc
        require = getattr(loc, "get_requires")
        if require is not None:
            self.requires(*require())
        return self
        
    @staticmethod
    def get(url, **params):
        new = request(url)
        new.loc = "request.get(%s, %s)" % (js_code(url), js_code(params))
        return new

    def code(self):
        return super(request, self).code()+";"
 
class Stateful(Dojo):
    """ Provides the ability to get and set named properties, including using 
    custom accessors in conjunction with the ability to monitor these 
    properties for changes.
    """
    require = ["dojo/Stateful"]
    


class topic(Dojo):
    """ Provides a centralized hub for publishing and subscribing to global 
    messages by topic.
    """
    require = ["dojo/topic"]
    
    def subscribe(self): pass
    def publish(self): pass
    

class router(Dojo):
    """ Provides the ability to map hash based structures to callbacks.
    """
    require = ["dojo/router"]
    
    def register(self): pass
    def publish(self): pass



class rpc(Dojo):
    """ methods to communicate via Remote Procedure Calls (RPC).
    """
    require = ["dojo/rpc"]



class node(Dojo):
    """ A loader plugin that is used to load “native” node.js modules.
    """
    require = ["dojo/node!"]

