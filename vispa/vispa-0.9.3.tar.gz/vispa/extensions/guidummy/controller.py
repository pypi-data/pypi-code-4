# -*- coding: utf-8 -*-

# imports
import cherrypy
import vispa.rpc
from vispa.controller import AbstractController

class GuiDummyController(AbstractController):

    def __init__(self):
        AbstractController.__init__(self)

    @cherrypy.expose
    @cherrypy.tools.workspace()    
    @cherrypy.tools.user()    
    def data(self):
        content = ""      
        return content
