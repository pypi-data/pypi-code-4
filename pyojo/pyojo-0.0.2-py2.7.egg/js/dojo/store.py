# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Dojo Store

    Memory
    JsonRest
    Cache
    Observable
    
    Not implemented:
    
    DataStore: compatibility with old API data/stores

"""
#from ..dojo import Dojo
#from .. import js_code

from pyojo.js import js_code, Object 
from _base import Dojo




class Store(Dojo):
    require = ["dojo/store/Memory"]
    
    
    
    
    def __init__(self, name, data):    
        self.name = name
        self.data = data
        
        self.loc = "%s = new Memory({data: [%s]," % (name, data)
        self.loc += "getChildren: function(object){return this.query({parent: object.id});}});"
        
    def get_json(self, url):    
        self.require +=["dojo/json", "dojo/text!"+url]
        self.loc = "%s = new Memory({data: [ json.parse(data) ]," % (self.name)
        self.loc += "getChildren: function(object){return object.children || [];}});"

        


FUNC={}
FUNC["Memory.getChildren.children"] = "function(object){return object.children || [];}});"
FUNC["Memory.getChildren.parent"] = "function(object){return this.query({parent: object.id});}"


class Memory(Object, Dojo):
    """
        
        x = new memory(options)
        
        :param data: string containing a Javascript array
        :param idProperty: identity property
        :param index:
        
        JS Methods:
        x.queryEngine
        
        x.add(object, options)
        x.get(id)
        x.getChildren(parent, options)
        x.getIdentity(object)
        x.getMetadata(object)
        x.put(object, options)
        x.query(query, options)
        x.remove(id)
        s.setData(data)
        x.transaction()
        
        @see http://dojotoolkit.org/api/1.9/dojo/store/Memory
    
    """
    
    require = ["dojo/store/Memory"]
      
    
    def __init__(self, name, data=None, json=None, **member):
        
        
        if json is not None:
            self.require +=["dojo/json", "dojo/text!"+json]
            self.data = "json.parse(data)"
        else:
            self.data = data
        
        member["data"] = self.data
    
        Object.__init__(self, **member)    
            
        
        #self.member.update(member)
        
        #self.new()
            
        #self.js = "%s = new Memory({data: [%s]," % (self.name, self.data)
        #self.js+= "getChildren: function(object){return object.children || [];}});"
        
    def add(self, data):
        self.loc_post +="%s.add(%s);" % (self.name, js_code(data))
        
    def remove(self, key):
        self.loc_post +="%s.remove('%s');" % (key)
        
    
    
class JsonRest(Object, Dojo):
    """ For larger data sets should use dojo.store.JsonRest etc. 
        instead of dojo.store.Memory
        
        x = new JsonRest(options)
        
        @param accepts: HTTP request accept header
        @param ascendingPrefix:
        @param descendingPrefix:
        @param headers:
        @param idProperty: identity property
        @param queryEngine:
        @param target:
        
        JS Methods:
        x.add(object, options)
        x.get(id)
        x.getChildren(parent, options)
        x.getIdentity(object)
        x.getMetadata(object)
        x.put(object, options)
        x.query(query, options)
        x.remove(id)
        x.transaction()
        
        @see http://dojotoolkit.org/api/1.9/dojo/store/Memory
    
    """
    
    require = ["dojo/store/JsonRest"]
    #options = ["",]
    #methods = []
    

    
    def X__init__(self, name=None, **options):    
        self.name = name
        self.options = options
        self.new()
        

        
