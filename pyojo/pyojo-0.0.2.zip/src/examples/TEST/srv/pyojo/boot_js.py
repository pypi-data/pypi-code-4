# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------

from pyojo import js


class Run(js.Dojo):
    require = ["pyojo/js/xml", "dojo/domReady!"]
    
    def code(self):
        return """xml.post(document.URL, {nav:navigator.appName, 
                                    ver:parseFloat(navigator.appVersion), 
                                    res:vx()+"x"+vy()});
        """


def GET(request):
    return js.Define(run=Run())








