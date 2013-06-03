# -*- coding: utf-8 -*-

# imports
import cherrypy
import vispa.rpc
from vispa.controller import AbstractController

class DemoController(AbstractController):

    def __init__(self):
        AbstractController.__init__(self)

    @cherrypy.expose
    def data(self):
        return 'demo'
