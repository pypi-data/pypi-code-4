# -*- coding: utf-8 -*-

import cherrypy
import uuid
import time

import vispa.rpc
from vispa.controller import AbstractController
from vispa import AbstractExtension

class TerminalController(AbstractController):

    def _terminal(self, id):
        return vispa.rpc.get(cherrypy.request.user, cherrypy.request.workspace, "vispa.extensions.terminal.remote.Terminal", id)
    
    @cherrypy.expose
    def open(self):
        id = str(uuid.uuid4())
        vispa.rpc.get(cherrypy.request.user, cherrypy.request.workspace, "vispa.extensions.terminal.remote.Terminal", id)
        return id

    @cherrypy.expose
    def close(self, id):
        vispa.rpc.clear(cherrypy.request.user, cherrypy.request.workspace, "vispa.extensions.terminal.remote.Terminal", id)

    @cherrypy.expose
    def command(self, id, command):
        terminal = self._terminal(id)  
        terminal.command(command)

    @cherrypy.expose
    def output(self, id):
        terminal = self._terminal(id)  
        cherrypy.response.headers['Content-Type'] = "application/json"
        return terminal.output() 

class TerminalExtension(AbstractExtension):

    def get_name(self):
        return 'terminal'

    def dependencies(self):
        return []

    def setup(self, extensionList):
        self.controller(TerminalController())
        self.js('js/extension.js')
        self.css('css/styles.css')
        self.remote()