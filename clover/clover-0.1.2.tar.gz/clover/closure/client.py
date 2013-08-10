import logging

from py4j.java_gateway import JavaGateway
from py4j.java_gateway import GatewayClient

logging.getLogger("py4j.java_gateway").setLevel(logging.INFO)

from clover.service import PORT, Service

class Client(object):
    gateway = None
    
    def __init__(self, port=None):
        if not Service.started:
            Service.start()
        logging.debug('Opening gateway')
        self.client = GatewayClient(port=PORT)
        self.gateway = JavaGateway(gateway_client=self.client)
    
    def clear(self, object):
        self.gateway.detach(object)
        
        
    def close(self):
        logging.debug('Closing gateway')
        #self.gateway.detach(self.klysanal)
        #self.client.close()
        #self.gateway.shutdown()
    
    
    def build_array(self, type, list):
        arr = self.gateway.new_array(type, len(list)) 
        for i, item in enumerate(list):
            arr[i] = item
        return arr
    
    def compile_soy(self, path, opts):
        output_file = self.gateway.compileSoy(path, opts)
        return open(output_file).read()
    
    def compile_inputs(self, output, externs, inputs, opts):
        return self.gateway.compileInputs(output, externs, inputs, opts)
    
    def new_sourcefile_from_code(self, filename, code):
        assert isinstance(code, str), "Code must be utf-8 encoded."
        return self.gateway.newSourceFileFromCode(filename, code)    
    
    def new_sourcefile_from_file(self, filename):
        return self.gateway.newSourceFileFromFilename(filename) 
    
    def new_soycompiler_options(self):
        return self.gateway.newSoyCompilerOptions()
    
    def new_location_mapping(self, a, b):
        return self.gateway.newLocationMapping(a, b)
    
    def new_compiler_options(self):
        return self.gateway.newCompilerOptions()
    
    def new_list(self):
        return self.gateway.jvm.java.util.ArrayList()
    
    def new_set(self, items):
        s = self.gateway.jvm.java.util.HashSet()
        
        for i in items:
            s.add(i)
        return s
    
    def new_map(self):
        return self.gateway.jvm.java.util.HashMap()