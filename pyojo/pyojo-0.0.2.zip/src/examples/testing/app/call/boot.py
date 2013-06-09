# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
""" Initial request suggested to the client.

    .. code-block:: javascript
    
        define(["pyojo/js/xml","dojo/domReady!"], 
          function(xml){
            return {
              run: function(){
                xml.post(document.URL, {nav:navigator.appName, 
                                        ver:parseFloat(navigator.appVersion), 
                                        res:vx()+"x"+vy()});
                //xml.get("/nabla/plugin_pyojo", {nav:navigator.appName, ver:parseFloat(navigator.appVersion), res:vx()+"x"+vy()});
                }
            }; 
"""



#js.Define({"run": run(), "log": log()})


from pyojo import js


class Run(js.Dojo):
    require = ["pyojo/js/xml", "dojo/domReady!"]
    
    
    def code(self):
        return """xml.post(document.URL, {nav:navigator.appName, 
                                    ver:parseFloat(navigator.appVersion), 
                                    res:vx()+"x"+vy()});
        """


def main():
    return js.Define(run=Run())#.code()


# ----------------------------------------------------------------------------
# Other 

def run():
    return """xml.post(document.URL, {nav:navigator.appName, 
                                    ver:parseFloat(navigator.appVersion), 
                                    res:vx()+"x"+vy()});
    """


def main1():
    
    define = js.Define(run=run())
    define.requires("pyojo/js/xml", "dojo/domReady!")    
    return define.code()