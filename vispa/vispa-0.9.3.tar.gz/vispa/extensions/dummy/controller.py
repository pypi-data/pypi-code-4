# -*- coding: utf-8 -*-

# imports
import cherrypy
import vispa.rpc
from vispa.controller import AbstractController

class DummyController(AbstractController):

    def __init__(self):
        AbstractController.__init__(self)

    @cherrypy.expose
    def data(self):
        content = ''

        # import the remote sys module
        service = vispa.rpc.get(cherrypy.request.user, cherrypy.request.workspace)
        rsys = service.getmodule('sys')
        content += '<p>sys.path: %s</p>' % rsys.path

        # the class 'DummyRPC' is located in the __init__.py file in remote/,
        # so we can create an instance of that class on remote-side
        dummyrpc = vispa.rpc.get(cherrypy.request.user, cherrypy.request.workspace, 'vispa.extensions.dummy.remote.DummyRpc')
        content += '<p>dummy: %s</p>' % dummyrpc.dummy()

        return content
