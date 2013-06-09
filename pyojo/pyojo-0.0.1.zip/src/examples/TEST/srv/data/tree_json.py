# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------

import pyojo
from pyojo import js, Error
from pyojo.js.lib.tree import DataTreeJSON, FileTreeJSON
"""
data = pyojo.data.Array()

#pyojo.model.data["tree"].root = {"name": "ROOT", "children":True}
#pyojo.model.data["tree"].child = {"name":"Child", "parent": "root"}

data["root"]={"id":"root", 
              "name":"Raiz", 
              "children":[{"id":"f1", "name":"Folder1", "children": True},
                          {"id":"f2", "name":"Folder2", "children": True}]}

#[{"id":"model", "name": "Models", "children":True},
#                                  {"id":"controller", "name": "Controllers", "children":True}]

data["f1"]={"id":"f1", "name": "Folder1", "children":[{"id":"file1", "name": "File"}]}
data["f2"]={"id":"f2", "name": "Folder2", "children":False}
"""






data = DataTreeJSON(key="root", name="Raiz")

data["root"] = {"key": "fo1", "name": "Folder1"}

data["fo1"] = {"key": "fi1", "name": "File1"}



def GET(request):
    return FileTreeJSON(pyojo.Config.url).get(request.param("item"))

def GET1(request):
    print "GET DATA %s %s" % (request.query, data[request.param("item")])
    return data[request.param("item")]

def POST(request):
    print "POST DATA %s" % request.query
    return data[request.param("item")]

def PUT(request):
    print "PUT DATA %s" % request.query
    return data[request.param("item")]

def DELETE(request):
    print "DELETE DATA %s" % request.query
    return data[request.param("item")]