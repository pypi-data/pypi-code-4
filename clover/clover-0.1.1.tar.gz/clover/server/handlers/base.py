from __future__ import absolute_import
import urlparse
import logging
import json

import webapp2
from jinja2 import Environment, FileSystemLoader
import os


__dir__ = os.path.dirname(os.path.abspath(__file__))
template_root = os.path.join(__dir__, '../')
template_env = Environment(
    loader=FileSystemLoader(template_root),
    auto_reload=True,  # do check if the source changed
    trim_blocks=True  # first newline after a block is removed
)

template_env.globals.update({
    'uri_for': webapp2.uri_for,
    
})

template_env.filters.update({
    'json': json.dumps,
    
})




class Base(webapp2.RequestHandler):
    def get_configs(self):
        return self.app.config.get('config').get_configs()
    
    def get_config(self, id):
        return self.app.config.get('config').get_config(id)
        #return self.configuration_map.get(id, None)
    
    def _handle_exception(self, exception, debug_mode):
        logging.exception(exception)
        self.data['exception'] = exception
        self.data['traceback'] = exception
        return self.render_error(500)
     
    def render_error(self, code, template=None):
        self.response.set_status(code)
        return self.render_template('templates/%s.html' % code)
    
    def render_template(self, name):
        global template_env
        template = template_env.get_template(name)
        self.response.out.write(template.render(**self.data))
        
    def render_template_string(self, string):
        template = template_env.from_string(string)
        self.response.out.write(template.render(**self.data))
        
    def initialize(self, request, response):
        global template_env
        super(Base, self).initialize(request, response)
        self.data = {}
        self.data['request'] = request
        self.data['current_uri'] = urlparse.urlsplit(request.url)