#logging.getLogger("py4j.java_gateway").setLevel(logging.INFO)

from service import Service

class Client(object):
    gateway = None
    
    def __init__(self, port=None):
        #client = GatewayClient(port=PORT)
        #self.gateway = JavaGateway(gateway_client=client)
        pass
    
    
    def build_array(self, type, list):
        arr = self.gateway.new_array(type, len(list)) 
        for i, item in enumerate(list):
            arr[i] = item
        return arr
    
    def compile_soy(self, path, opts):
        print "cOMPILESOY"
        output_file = Service.service_class.compileSoy(path, opts)
        return open(output_file).read()
    
    def compile_inputs(self, output, externs, inputs, opts):
        return Service.service_class.compileInputs(output, externs, inputs, opts)
    
    def new_sourcefile_from_code(self, filename, code):
        assert isinstance(code, str), "Code must be utf-8 encoded."
        return Service.service_class.newSourceFileFromCode(filename, code)    
    
    def new_sourcefile_from_file(self, filename):
        
        return Service.service_class.newSourceFileFromFilename(filename) 
    
    def new_soycompiler_options(self):
        import jpype
        #inst = Service.service_class()
        print "NEW SOY COMPILER OPTS", jpype.JPackage('clover').Service()
        return inst.newSoyCompilerOptions()
    
    def new_location_mapping(self, a, b):
        return Service.service_class.newLocationMapping(a, b)
    
    def new_compiler_options(self):

        return  Service.service_class.newCompilerOptions()
    
    def new_list(self):
        return []
    
    def new_set(self, items):
        return null
    
    def new_map(self):
        return self.gateway.jvm.java.util.HashMap()