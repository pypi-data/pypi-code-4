# -*- coding: utf-8 -*-

# imports
import cherrypy
from ws4py.server.cherrypyserver import WebSocketTool


class WSTool(WebSocketTool):

    def __init__(self, *args, **kwargs):
        WebSocketTool.__init__(self, *args, **kwargs)
        self.__platform = None

    def set_platform(self, platform):
        self.__platform = platform

    def upgrade(self, *args, **kwargs):
        super(WSTool, self).upgrade(*args, **kwargs)
        setattr(cherrypy.serving.request.ws_handler, 'platform', self.__platform)
