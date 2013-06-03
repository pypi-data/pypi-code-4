# -*- coding: utf-8 -*-

# imports
import os.path
import cherrypy
from mako import exceptions
from mako.template import Template


class MakoTool(cherrypy.Tool):

    def __init__(self, common):
        cherrypy.Tool.__init__(self, 'before_handler', self._render, priority=100)
        self.common = common

    def _render(self, template=None, subfolder=None, extension_name=None):
        request = cherrypy.serving.request
        request._mako_inner_handler = request.handler
        request._mako_template = template
        request._mako_subfolder = subfolder
        request._mako_extension_name = extension_name
        request.handler = self._do_render

    def _do_render(self, *args, **kwargs):
        data = cherrypy.serving.request._mako_inner_handler(*args, **kwargs)

        if not isinstance(data, dict):
            return exceptions.html_error_template().render(error='Template data is no dict: %s' % str(type(cherrypy.response.body)))

        if not cherrypy.serving.request._mako_extension_name and not cherrypy.serving.request._mako_subfolder:
            cherrypy.serving.request._mako_subfolder = 'html'

        makotemplate = cherrypy.engine.publish('lookup_template', cherrypy.serving.request._mako_template, cherrypy.serving.request._mako_subfolder, cherrypy.serving.request._mako_extension_name).pop()
        if not makotemplate:
            return exceptions.html_error_template().render(error='Template not present')

        data.update(self.common)
        try:
            return makotemplate.render(**data)
        except:
            return exceptions.html_error_template().render(error='Error while rendering template with given data: %s' % str(data))