# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
import os
import pyojo
from pyojo.all import *


class Array(dict, js.Code):
    
    def __str__(self):
        return self.code()
    
    def __repr__(self):
        return "<Array %s>" % self.code()
    
        
    def code(self):
        code = ""
        for key, value in self.iteritems():
            code += "%s: %s, " % (key, js.js_code(value))
        return "{"+code[:-2]+"}"
        
        

def FileScan(path):
    print "FileScan", path
    data=[] 
    root_id="root"
    for root, dirs, files in os.walk(path):
        folder = root.replace(path, "")
        folder_id = folder.replace(os.path.sep,"_")
        folder_url = folder.replace(os.path.sep, "/")
        folder_name = folder.rsplit(os.path.sep,1)[-1]
        
        if folder_id=="":
            data.append(Array(name = "Root", 
                              id = root_id,
                              url = "", 
                              root = True))
        else:
            data.append({"name": folder_name,
                         "id": root_id + folder_id, 
                         "url": folder_url, 
                         "parent": root_id + folder_id.rsplit("_",1)[0]})
        
        print folder
        for name in files:
            if os.path.splitext(name)[1] in [".pyc", ".pyo"]: 
                continue
            
            file = os.path.join(folder, name)
            file_id = file.replace(os.path.sep,"_")
            if file.endswith(".py"):
                file_name= ".".join(name[:-3].rsplit("_", 1))
            file_url = os.path.join(folder, file_name).replace(os.path.sep, "/")
            
            data.append({"name": file_name, 
                         "id": folder_id+file_id, 
                         "url": file_url, 
                         "parent": "root" +folder_id})
        
            print file
    return data

DATA="1"

"""store = dojo.store.Store("myStore", DATA)
    tree = dijit.Tree("arbol", target="tree")
    tree.store("myStore", "root")
    return store, tree
"""

xx = Array(a=1, b=True, c="h")
print xx.code()

def GET(request):
    #request.content_type("text/plain")
    code = store.Memory("MyStore",data=FileScan(request.config.url)).code()

    
    return pyojo.html_highlighter(pyojo.jsbeautify(code))