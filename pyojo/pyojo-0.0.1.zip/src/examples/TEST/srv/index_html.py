# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo.examples                                  Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------

from pyojo.all import *

INDEX="""
<html>
<head>
<title>pyojo server</title>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
<link rel="StyleSheet" type="text/css" href="//ajax.googleapis.com/ajax/libs/dojo/1.9.0/dijit/themes/claro/claro.css">
<link rel="StyleSheet" type="text/css" href="static/css/pyojo.css">
<script type="text/javascript" src="/static/js/shjs/sh_main.min.js"></script>
<script type="text/javascript" src="/static/js/shjs/lang/sh_javascript.min.js"></script>
<link type="text/css" rel="stylesheet" href="/static/js/shjs/css/sh_ide-eclipse.css">
</head>
<body id="base" class="claro">
<script src="//ajax.googleapis.com/ajax/libs/dojo/1.9.0/dojo/dojo.js" 
data-dojo-config="async: true, packages: [{name: 'pyojo', location: '/pyojo'}]">
// Server info:
// 127.0.0.1 Development/1.0
// python 2.7.2 (default, Jun 12 2011, 15:08:59) [MSC v.1500 32 bit (Intel)]
// Client info:
// Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0
</script><script>
// Pyojo (c)2012 nabla.net
var app_path = "F:\Google Drive\Projects\python\gapp\vanstats";
var app_user = "";
var app_hash = "B6589FC6";
document.cookie='state_hash='+app_hash+'; path=/';
document.cookie='state_check='+app_hash+'; path=/';
require(["pyojo/js/init", "pyojo/boot", "dojo/domReady!"], 
function(init, boot){boot.run()});
</script>
</body>
</html>
"""


def GET(request):
    return INDEX


def POST(request):
        
    request.content_type("application/xml")
    
    nav = request.param('nav')
    ver = request.param('ver')
    res = request.param('res')
        
    reply = pyojo.ScriptXML()
        
    module = pyojo.import_url(request.config.url, "/pyojo/base.js")
    code = module.GET(request)
    code.add('log("Dojo Toolkit version "+dojo.version);')
    code.add('status("%s %s %s");' % (nav,ver,res))
    code.add(js.Dojo().script("gui.run();").requires("pyojo/gui", "dojo/domReady!")  )
      
        
    reply.code(code.code()) #base llama a gui
    return reply
