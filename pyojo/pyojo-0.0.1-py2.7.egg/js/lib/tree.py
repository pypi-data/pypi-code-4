# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
""" Javascript Tree code blocks.

"""

import os
import urllib2
from pyojo.data import MIMETYPE
from pyojo import js, Error
from pyojo.js import dojo
from pyojo.js import dijit
from pyojo.js.dojo.store import JsonRest
from pyojo.js.dijit.model import ObjectStoreModel

class TreeJSON(js.Block):
    """ A tree widget for JSON data.
    """
    _z = js.Function("fullObject", 
                     "return fullObject.children;")
            
    getChildren = js.Function("object", 
                              "return this.get(object.id).then(%s);" % _z)

    getRoot = js.Function("onItem", 
                          "this.store.get('root').then(onItem);")
    
    mayHaveChildren = js.Function("object", 
                                  "return 'children' in object;")

    def __init__(self, data_source, dnd=False):
        
        super(TreeJSON, self).__init__("TreeJSON")
        store = JsonRest(target = data_source,
                         getChildren = self.getChildren)
        self.tree_data = js.Var("tree_data", store)

        model = ObjectStoreModel(
                                store = self.tree_data.var,
                                getRoot = self.getRoot,
                                mayHaveChildren = self.mayHaveChildren 
                                )
        self.tree_model = js.Var("tree_model", model)
        
        self.tree = dijit.Tree("TREE_Tree", 
                      model=self.tree_model.var, 
                      target="TREE")
        if dnd:
            self.tree.member["dndController"]=js.Code("dndSource")
            self.tree.require.append("dijit/tree/dndSource")
        
        self.blocks = [self.tree_data, 
                       self.tree_model, 
                       self.tree,
                       "status('Tree ready.');"]
    

        
    def onclick(self, function):
        self.tree.member["onClick"] = self.get_code(function)


class DataTreeJSON(dict):
    """ A special dictionary for TreeJSON data. 
    """
    def __init__(self, **kwargs):

        self.parent = {}
        self.key_set(None, **kwargs)
        super(DataTreeJSON, self).__init__()

    def key_set(self, parent, **kwargs):
        keys = kwargs.keys()
        if not "key" in keys:
            raise Error("key is needed")
        key = kwargs.pop("key")
        super(DataTreeJSON, self).__setitem__(key, dict(**kwargs))
        if parent is not None:
            self.parent[key] = parent

    def key_get(self, key, child=True):
        more = {"id": key}
        value = self.get(key, None)
        if value is None:
            return ""
        if child:
            more["children"] = []
            for child, par in self.parent.iteritems():
                if par == key:
                    more["children"].append(self.key_get(child, False))
            if len(more["children"]) == 0:
                more["children"] = False
        else:
            if key in self.parent.values():
                more["children"] = True
        value.update(more)
        return value

    def __getitem__(self, _key):
        return self.key_get(_key)

    def __setitem__(self, _key, values):
        self.key_set(_key, **values)  



class FileTreeJSON(object):
    """ Expose a file structure to a TreeJSON. 
    """
    def __init__(self, path):
        self.path = os.path.abspath(path)

    def get(self, item=None):
        if item is None or item=="root":
            root = ""
            path = self.path
            data = {"id": "root", "name": "/"}
        else:
            root = urllib2.unquote(item)
            path = os.path.join(self.path, root)
            data = {"id": item, "name": root}

        data["children"] = []
        
        folders = []
        files = []
                        
        for name in os.listdir(path):
            ext = os.path.splitext(name)[1][1:]
            if ext in ["pyc", "pyo"]: 
                continue
            fullpath = os.path.join(self.path, root, name)
            key = urllib2.quote(os.path.join(root, name))
            if ext == "py" and "_" in name:
                name = ".".join(name.split(".")[0].rsplit("_",1))
                ext = os.path.splitext(name)[1][1:]
            found = {"id":key, "name": name}
            if os.path.isdir(fullpath):
                if len(os.listdir(fullpath))>0:
                    found["children"] = True
                else:
                    found["children"] = []
                folders.append(found)
            else:
                files.append(found)
                url = os.path.join(root, name).replace(os.path.sep, "/")
                if url[0] != "/": url = "/" + url
                found["url"] = url
            if MIMETYPE.has_key(ext):
                found["ctype"] = MIMETYPE[ext]
            else:
                found["ctype"] = "undefined"
                
        
        folders.sort()
        files.sort()
        data["children"] += folders
        data["children"] += files
        return data
    
    
    