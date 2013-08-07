from __future__ import absolute_import
import logging
from clover.closure.compiler import Compiler
from clover.service import Service

logger = logging.getLogger('clover.Builder')



class Builder(object):
    def __init__(self, config):
        self.config = config
        self.compiler = Compiler()

    def build(self):
        service = Service()
        service.start()
        
        config = self.config
        manifest = config.get_build_manifest()
        deps = manifest.get_sorted_deps()
        
        # prepend base.js
        base = manifest.get_base_js()
        if base is None:
            raise Exception("base.js not found.")
        logger.info('Using base.js from %s', base)
        deps.insert(0, base)

        #logging.debug(deps)

        self.compiler.set_sources(deps)
        self.compiler.set_config(self.config)
        result = self.compiler.compile()

        return result