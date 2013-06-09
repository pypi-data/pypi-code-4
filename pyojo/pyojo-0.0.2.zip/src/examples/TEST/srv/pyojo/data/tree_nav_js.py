# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
import pyojo

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

JS = """
require([
     "dojo/_base/window", "dojo/store/Memory",
     "dijit/tree/ObjectStoreModel", "dijit/Tree",
     "dojo/domReady!"
 ], function(win, Memory, ObjectStoreModel, Tree){

     // Create test store, adding the getChildren() method required by ObjectStoreModel
     var myStore = new Memory({
         data: [
            { id: 1, name: 'Dijit Tree API', 
            url: 'http://dojotoolkit.org/api/1.6/dijit.Tree', root: true },
            { id: 2, name: 'Dijit Tree.model API', 
            url: 'http://dojotoolkit.org/api/1.6/dijit.Tree.model', parent: 1 },
            { id: 3, name: 'Dijit Tree.ForestStoreModel API', url: 'http://dojotoolkit.org/api/1.6/dijit.tree.ForestStoreModel', parent: 1 },
            { id: 4, name: 'Dijit Tree.TreeStoreModel API', url: 'http://dojotoolkit.org/api/1.6/dijit.tree.TreeStoreModel', parent: 1 },
         ],
         getChildren: function(object){
             return this.query({parent: object.id});
         }
     });

     // Create the model
     var myModel = new ObjectStoreModel({
         store: myStore,
         query: {root: true}
     });

     // Create the Tree, specifying an onClick method
     (new Tree({
         model: myModel,
         onClick: function(item){
             // Get the URL from the item, and navigate to it
             location.href = item.url;
         }
     })).placeAt('VIEW').startup();
     status('Pruena Navi');
});
"""

from pyojo import js

def GET(request):
    return js.Code(JS)
