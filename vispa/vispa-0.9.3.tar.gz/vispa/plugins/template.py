# -*- coding: utf-8 -*-

from cherrypy.process.plugins import SimplePlugin
from mako.lookup import TemplateLookup
import os

__all__=['MakoPlugin']

class MakoPlugin(SimplePlugin):

    def __init__(self, bus, base_dir=None, module_dir=None, collection_size=50, encoding='utf-8'):
        SimplePlugin.__init__(self, bus)
        self.bus.listeners.setdefault('lookup_template', set())
        self.base_dir = base_dir
        self.module_dir = module_dir
        self.encoding = encoding
        self.collection_size = collection_size
        self.lookup = None

    def start(self):
        self.lookup = TemplateLookup(directories=self.base_dir,
                                     module_directory=self.module_dir,
                                     input_encoding=self.encoding,
                                     output_encoding=self.encoding,
                                     collection_size=self.collection_size)

    def stop(self):
        del self.lookup

    def lookup_template(self, name, subfolder=None, extension_name=None):
        subfolder = subfolder or ''
        if not extension_name:
            return self.lookup.get_template(os.path.join('templates', subfolder, name))
        else:
            return self.lookup.get_template(os.path.join('extensions', extension_name, 'templates', subfolder, name))
