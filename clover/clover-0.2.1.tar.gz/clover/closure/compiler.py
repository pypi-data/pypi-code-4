from __future__ import absolute_import
import logging
import tempfile
import time

import os

from clover import get_package_resource
from clover.closure.client import Client
from clover.closure.outputmanifest import OutputManifest
from clover.service import Service

__dir__ = os.path.dirname(os.path.abspath(__file__))

logger = logging.getLogger('clover.Compiler')

DEFAULT_EXTERNS = [
    # JS externs
    "es3.js",
    "es5.js",

    # Event APIs
    "w3c_event.js",
    "w3c_event3.js",
    "gecko_event.js",
    "ie_event.js",
    "webkit_event.js",
    "w3c_device_sensor_event.js",

    # DOM apis
    "w3c_dom1.js",
    "w3c_dom2.js",
    "w3c_dom3.js",
    "gecko_dom.js",
    "ie_dom.js",
    "webkit_dom.js",

    # CSS apis
    "w3c_css.js",
    "gecko_css.js",
    "ie_css.js",
    "webkit_css.js",

    # Top-level namespaces
    "google.js",

    "deprecated.js",
    "fileapi.js",
    "flash.js",
    "gears_symbols.js",
    "gears_types.js",
    "gecko_xml.js",
    "html5.js",
    "ie_vml.js",
    "iphone.js",
    "webstorage.js",
    "w3c_anim_timing.js",
    "w3c_css3d.js",
    "w3c_elementtraversal.js",
    "w3c_geolocation.js",
    "w3c_indexeddb.js",
    "w3c_navigation_timing.js",
    "w3c_range.js",
    "w3c_selectors.js",
    "w3c_xml.js",
    "window.js",
    "webkit_notifications.js",
    "webgl.js"
]


class Compiler(object):
    """ Compiles a list of sources.
    """
    sources = None
    location_prefix = ""
    
    def __init__(self, client=None):
        self.client = client if client else Client()

    def set_sources(self, sources):
        self.sources = sources

    def set_config(self, config):
        self.config = config

    def set_compiler_options(self, options):
        self.compiler_options = options
        
    def set_externs(self, externs):
        self.externs = externs
        
    def set_inputs(self, inputs):
        self.inputs = inputs
        
    def compile(self):
        if self.sources is None:
            raise Exception("Sources isnt set")

        Service.start()

        config = self.config
        client = self.client
        
        logger.info('Preparing compilation..')

        logger.info('New options..')

        options = client.new_compiler_options()
        
        logger.info('Applying options..')
        
        config.apply_compiler_options(options, client)

        #// Add location mapping for paths in source map.
        #// TODO: Allow an option for generating the "sourceRoot" member in source 
        #// maps. See http://code.google.com/p/closure-compiler/issues/detail?id=770
        mapping = client.new_location_mapping("", self.location_prefix)
        location_mappings = client.new_list()
        location_mappings.append(mapping)
        options.setSourceMapLocationMappings(location_mappings)

        externs = client.new_list()

        use_default_externs = True

        if use_default_externs:
            for path in DEFAULT_EXTERNS:
                path = get_package_resource(os.path.join('javascript', 'externs', path))
                sourcefile = client.new_sourcefile_from_file(path)
                externs.append(sourcefile)

        user_externs = config.read_option(config.options.externs)
        if user_externs:
            for path in user_externs:
                if path.startswith('//'):
                    path = get_package_resource(os.path.join('javascript', 'externs', 'contrib', *path[2:].split('/')))
                else:
                    path = config.abspath(path)
    
                sourcefile = client.new_sourcefile_from_file(path)
                externs.append(sourcefile)


        # transform sources to java objects
        inputs = client.new_list()

        for source in self.sources:
            sourcefile = source.build_sourcefile(client)
            inputs.append(sourcefile)

        logger.debug('using inputs %s', len(inputs))

        start = time.time()
        
        outputDir = tempfile.mkdtemp()
        
        logger.info('Compiling...')
        
        client.compile_inputs(outputDir, externs, inputs, options)
        
        logger.info('Compilation finished. %s', time.time() - start)

        for ext in externs:
            client.clear(ext) 
            
        for inp in inputs:
            client.clear(inp)
            
        client.clear(externs)
        client.clear(inputs)
        client.clear(options)
        
        #logging.debug('N objects %s', len(gc.get_objects()))
        
        client.close()
        
        return OutputManifest(os.path.join(outputDir, 'manifest.json'))