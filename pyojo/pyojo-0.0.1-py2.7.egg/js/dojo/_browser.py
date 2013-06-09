# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# pyojo                                            Copyright (c) 2011 nabla.net
#------------------------------------------------------------------------------
""" Client browser utilities.



"""
# dojo/_base/url -> require.toUrl()

from _base import Dojo


  
 
class window(Dojo):
    """ Functions related to the viewport.
    """
    require = ["dojo/window"]
    def getBox(self): pass
    def get(self): pass
    def scrollIntoView(self): pass    
    pass


class cookie(Dojo):
    """ Handling client side cookies.
    """
    require = ["dojo/cookie"]
    

class has(Dojo):
    """ Provides standardized feature detection.
    """
    require = ["dojo/has"] 


class sniff(Dojo):
    """ Browser feature detection.
    """
    require = ["dojo/sniff"]
    

class back(Dojo):
    """ Allows you to update the browser history, so that it’s possible to 
    use the Back and Forward buttons.
    """
    require = ["dojo/back"]
    
    def init(self): pass
    def addToHistory(self): pass
    

class hash(Dojo):
    """ Aprovides methods for monitoring and updating the hash (history) 
    in the browser URL.
    """
    require = ["dojo/back"]


class colors(Dojo):
    """ Augments the base dojo/_base/Color class with additional methods and 
    named colors.
    """
    require = ["dojo/colors"]


    
class hccss(Dojo):
    """ Provides “High Contrast” feature detection for accessibility purposes.
    """
    require = ["dojo/hccss"]


