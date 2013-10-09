from __future__ import absolute_import
from clover.closure.client import Client

class SoyCompiler(object):
    def __init__(self):
        pass
    
    def compile(self, path):
        client = Client()
        opts = client.new_soycompiler_options()
        code = client.compile_soy(path, opts)
        
        #client.close()
        return code
