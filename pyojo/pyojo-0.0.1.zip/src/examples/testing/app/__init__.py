# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# nabla                              Copyright (c) 2013 Jose M. Vicente Segura
# ----------------------------------------------------------------------------

""" Default web application skeleton.
"""

import os
import pyojo
from pyojo import Config, TAG, log


PATH = os.path.dirname(os.path.realpath(__file__))
PATH_URL = os.path.join(PATH, "url")



@pyojo.route("/boot")
class Index(pyojo.Reply):
    
    def GET(self):
        return self.request.static("index.html")
        #return [str(pyojo.app.index("boot.run()"))]

    def POST(self):
        """ First call defined in module call.boot
        
            1 Import the base module.
            2 Suggest a GUI
            
        """
        nav = self.request.param('nav')
        ver = self.request.param('ver')
        res = self.request.param('res')
        
        reply = pyojo.ScriptXML()
        
        module = pyojo.import_path(pyojo.app.PATH, "base")
        
        code = module.main()
        code.add('status("%s %s %s");' % (nav,ver,res))
        
        
        reply.code(code.code()) #base llama a gui
        
        #module = pyojo.import_path(pyojo.app.PATH, "gui")
        #reply.code(module.main())
        #reply.call("gui") viene demasiado pronto, ho hay nodo panel
        
        #reply.call("ready")
        #reply.call("base") # Impors       
        return reply
    

        
        
        


        
        return reply



@pyojo.route("/", accept="text/html")
def pyojo_default_home_page(request):
    """ Returns the index page from static folder.
    """
    return request.static("/index.html")

@pyojo.route("/pyojo/js/{script}", "GET", "applicattion/javascript")
def pyojo_default_js_static(request, script): #environ, start_response
    """ Returns a javascript file.
    """
    return request.static(request.url)


@pyojo.route("/pyojo/{command}")
def pyojo_default_call(request, command):
    """ Returns javascript code returned from module call/command.main()
    """
    #url = request.url.replace("/pyojo/", "")
    #code = "alert('Holita %s');" % url
    call = command.replace(".js", "")
    try:
        module = pyojo.import_path(PATH, call)
        code = module.main()
    except pyojo.ModuleNotFoundError, e:
        code = repr(e)
    request.content_type("text/javascript")
    return code



@pyojo.route("/", method="POST", accept="*/xml")
@pyojo.route("/home", method="POST", accept="*/xml")
@pyojo.route("/index", method="POST", accept="*/xml")
def pyojo_default_boot(request):
    """ Standard boot sequence.
    
        Should have query parameters to decide the GUI type.
        
        If navigator is big, return call/base.
        
    """
    reply = pyojo.ScriptXML()
    reply.code("status('"+request.url+"');")
    reply.call("ready")
    reply.call("base")
    return reply


# ----------------------------------------------------------------------------

INDEX="""
<html>
<head>
<title>pyojo server</title>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon">
<link rel="StyleSheet" type="text/css" href="static/js/dojo/dijit/themes/claro/claro.css">
<link rel="StyleSheet" type="text/css" href="static/css/pyojo.css">
</head>
<body id="base" class="claro">
<script src="static/js/dojo/dojo/dojo.js" 
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
@pyojo.route("/home", accept="text/html")
def pyojo_home_page_testing_1(request):
    """ Returns html from string.
    """
    request.content_type("text/html")
    return [INDEX]


# ----------------------------------------------------------------------------

def _index(call="boot.run()"):
    
    dojo_config = "async: true, packages: [{name: 'pyojo', location: '/pyojo'}]"

    dojo_local = "static/js/dojo/"
    dojo_file = dojo_local + "dojo/dojo.js" 
    
    if os.path.exists(os.path.join(Config.www, dojo_file)) and False:
        log.info("Dojo Toolkit from %s", dojo_file)
    else:
        dojo_path = Config.ini.get("WEB", "Dojo_CDN")
        print "CDN %s" % dojo_path
        dojo_file = dojo_path + "/dojo/dojo.js" 
        log.info("Dojo Toolkit from %s", dojo_file)
        
    init="""// Pyojo (c)2012 nabla.net
    var app_path = "F:\Google Drive\Projects\python\gapp\vanstats";
    var app_user = "";
    var app_hash = "B6589FC6";
    document.cookie='state_hash='+app_hash+'; path=/';
    document.cookie='state_check='+app_hash+'; path=/';
    require(["pyojo/js/init", "pyojo/boot", "dojo/domReady!"], 
    function(init, boot){%s});
    """ % (call)
    
    
    script_dojo = TAG("script")({"src": dojo_file,
                                 "data-dojo-config": dojo_config})
    script_dojo +=" "
    script_init = TAG("script")
    script_init += init
    
    html = TAG("html")
    html.head.title += "Pyojo Application"
    html.head.meta({"http-equiv":"content-type",
                    "content":"text/html; charset=utf-8"})
    html.head += TAG("link")({"rel":"shortcut icon",
                              "href":"/favicon.ico",
                              "type":"image/x-icon"})
    html.head += TAG("link")({"rel":"StyleSheet",
                              "href":"static/css/pyojo.css",
                              "type":"text/css"})
    html.head += TAG("link")({"rel":"StyleSheet",
                              "href":dojo_path+"dijit/themes/claro/claro.css",
                              "type":"text/css"})
    html.body.id = "base"
    html.body += script_dojo
    html.body += script_init
    return html


@pyojo.route("/index", accept="text/html")
def _pyojo_home_page_testing_generation(request):
    """ Testing the web page HTML generator.
    
        TODO: link and meta </> semms to break the page
    """
    
    return [str(_index())]






"""
@pyojo.route("/pyojo2/{command}", "pyojo")
def CMD(request): #environ, start_response
    return "alert('hola');"
"""

