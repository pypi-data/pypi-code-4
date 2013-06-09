# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
import pyojo
print "TREE TEST"

data = pyojo.Array()

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

HTML = '''
<!DOCTYPE html>
<html >
<head>

    <link rel="stylesheet" href="/static/js/dojo/dijit/themes/claro/claro.css">
    
    <script>dojoConfig = {parseOnLoad: true}</script>
    <script src='/static/js/dojo/dojo/dojo.js'></script>
    
    <script>
require([
    "dojo/aspect", "dojo/_base/window", "dojo/store/Memory", "dojo/store/Observable",
    "dijit/Tree", "dijit/tree/ObjectStoreModel", "dijit/tree/dndSource",
    "dojo/domReady!"
], function(aspect, win, Memory, Observable, Tree, ObjectStoreModel, dndSource){

    // Create test store.
    store = new Memory({
        data: [
            { id: 'world', name:'The earth', type:'planet', population: '6 billion'},
            { id: 'AF', name:'Africa', type:'continent', population:'900 million', area: '30,221,532 sq km',
                    timezone: '-1 UTC to +4 UTC', parent: 'world'},
                { id: 'EG', name:'Egypt', type:'country', parent: 'AF' },
                { id: 'KE', name:'Kenya', type:'country', parent: 'AF' },
                    { id: 'Nairobi', name:'Nairobi', type:'city', parent: 'KE' },
                    { id: 'Mombasa', name:'Mombasa', type:'city', parent: 'KE' },
                { id: 'SD', name:'Sudan', type:'country', parent: 'AF' },
                    { id: 'Khartoum', name:'Khartoum', type:'city', parent: 'SD' },
            { id: 'AS', name:'Asia', type:'continent', parent: 'world' },
                { id: 'CN', name:'China', type:'country', parent: 'AS' },
                { id: 'IN', name:'India', type:'country', parent: 'AS' },
                { id: 'RU', name:'Russia', type:'country', parent: 'AS' },
                { id: 'MN', name:'Mongolia', type:'country', parent: 'AS' },
            { id: 'OC', name:'Oceania', type:'continent', population:'21 million', parent: 'world'},
                { id: 'AU', name:'Australia', type:'country', population:'21 million', parent: 'OC'},
            { id: 'EU', name:'Europe', type:'continent', parent: 'world' },
                { id: 'DE', name:'Germany', type:'country', parent: 'EU' },
                { id: 'FR', name:'France', type:'country', parent: 'EU' },
                { id: 'ES', name:'Spain', type:'country', parent: 'EU' },
                { id: 'IT', name:'Italy', type:'country', parent: 'EU' },
            { id: 'NA', name:'North America', type:'continent', parent: 'world' },
                { id: 'MX', name:'Mexico', type:'country',  population:'108 million', area:'1,972,550 sq km',
                        parent: 'NA' },
                    { id: 'Mexico City', name:'Mexico City', type:'city', population:'19 million', timezone:'-6 UTC', parent: 'MX'},
                    { id: 'Guadalajara', name:'Guadalajara', type:'city', population:'4 million', timezone:'-6 UTC', parent: 'MX' },
                { id: 'CA', name:'Canada', type:'country',  population:'33 million', area:'9,984,670 sq km', parent: 'NA' },
                    { id: 'Ottawa', name:'Ottawa', type:'city', population:'0.9 million', timezone:'-5 UTC', parent: 'CA'},
                    { id: 'Toronto', name:'Toronto', type:'city', population:'2.5 million', timezone:'-5 UTC', parent: 'CA' },
                { id: 'US', name:'United States of America', type:'country', parent: 'NA' },
            { id: 'SA', name:'South America', type:'continent', parent: 'world' },
                { id: 'BR', name:'Brazil', type:'country', population:'186 million', parent: 'SA' },
                { id: 'AR', name:'Argentina', type:'country', population:'40 million', parent: 'SA' }
        ]
    });

    // Since dojo.store.Memory doesn't have various store methods we need, we have to add them manually
    store.getChildren = function(object){
        // Add a getChildren() method to store for the data model where
        // children objects point to their parent (aka relational model)
        return this.query({parent: this.getIdentity(object)});
    };
    aspect.around(store, "put", function(originalPut){
        // To support DnD, the store must support put(child, {parent: parent}).
        // Since our store is relational, that just amounts to setting child.parent
        // to the parent's id.
        return function(obj, options){
            if(options && options.parent){
                obj.parent = options.parent.id;
            }
            return originalPut.call(store, obj, options);
        }
    });

    // Wrap the store in Observable so that updates to the store are reflected to the Tree
    store = new Observable(store);

    // Create the model and tree
    model = new ObjectStoreModel({store: store, query: {id: 'world'}});
    tree = new Tree({
        model: model,
        dndController: dndSource
    }).placeAt(win.body());
});
    </script>
</head>
<body class="claro">
    
</body>
</html>
'''

def GET(request):
    return HTML
    print "GET DATA %s" % request.query
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