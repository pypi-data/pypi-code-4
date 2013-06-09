# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# pyojo                                            Copyright (c) 2011 nabla.net
#------------------------------------------------------------------------------
""" Data management utilities.  
"""
# dojo/_base/url -> require.toUrl()

from _base import Dojo


#------------------------------------------------------------------------------
#--- Data


class string(Dojo):
    """ Provides some simple string manipulation utilities.
    """
    require = ["dojo/string"]


class date(Dojo):
    """ Provides date handling functions.
    """
    require = ["dojo/date"]


class text(Dojo):
    """ AMD plugin that loads arbitrary string data from a file and returns it.
    """
    require = ["dojo/text!"]


class json(Dojo):
    """ JSON parsing and serialization.
    """
    require = ["dojo/json"]
    
    def parse(self): pass
    def stringfy(self): pass


class ioQuery(Dojo):
    """ Functions for converting between JavaScript objects and query strings 
    that are part of a URL.
    """
    require = ["dojo/io-query"]
    
    def objectToQuery(self): pass
    def queryToObject(self): pass

    



#------------------------------------------------------------------------------
#--- Internationalization


class i18n(Dojo):
    """ A module that provides internationalization features.
    """
    require = ["dojo/i18n!"] 


    
class number(Dojo):
    """ Methods for user presentation of JavaScript Number objects: formatting, 
    parsing, and rounding.
    """
    require = ["dojo/number"] 
    
    
class currency(Dojo):
    """ Handling of virtually every type currency according to local customs.
    """
    require = ["dojo/currency"] 
 

class cldr(Dojo):
    """ Contains data from the Common Locale Data Repository (CLDR).
    """
    require = ["dojo/cldr"] 
