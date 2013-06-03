# -*- coding: utf-8 -*-

# imports
import cherrypy
import vispa
import logging

logger = logging.getLogger(__name__)

class PrivateParameterFilter(cherrypy.Tool):

    def __init__(self):
        cherrypy.Tool.__init__(self, 'before_handler', self.before_handler, priority=55)

    def before_handler(self):
        private_params = {}
        for key in cherrypy.request.params.keys():
            if key.startswith('_'):
                private_params[key] = cherrypy.request.params.pop(key)
        cherrypy.request.private_params = private_params
