from __future__ import absolute_import
import logging

from clover.sourcefiles.javascript import JavascriptSourceFile
from clover.closure.soycompiler import SoyCompiler

logger = logging.getLogger('clover.sourcefiles.soy')

class SoySourceFile(JavascriptSourceFile):
    precompile = True
    _compile_cache = None
    
    def get_code(self):
        logger.info('Compiling soy template: %s', self.path)
        if self._compile_cache is None or self.is_cache_expired():
            self._compile_cache = SoyCompiler().compile(self.path)
        return self._compile_cache  