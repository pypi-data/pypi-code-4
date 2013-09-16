import functools



class APIDescription(object):
    name = ''
    version = ''
    description = ''
    
    def __init__(self):
        self.method_map = {}
        
    def get_method_information(self, method_id):
        return self.method_map.get(method_id)
    
    def add_class(self, service_class):
        """ Add package (and its methods to method map).
        """
        if not hasattr(service_class, '__package_information'):
            raise Exception("invalid service class")
        
        # TODO: check if already added
        
        map(functools.partial(self.check_add_method, service_class), service_class.__dict__.values())
    
    def check_add_method(self, service_class, method):
        """ Add method fqn to method map. 
        """
        if not hasattr(method, '__method_information'):
            return
        
        # TODO: check if already added
        
        method_info = getattr(method, '__method_information')
        package_info = getattr(service_class, '__package_information')
        
        # add the package class so we can resolve method calls easily
        method_info.service_class = service_class 
        
        method_name = '%s.%s.%s' % (self.name, package_info.name, method_info.name)
        
        self.method_map[method_name] = method_info
        
    def to_directoryitem_json(self):
        """ convert to a directory item json
        """
        pass
        
    def to_restdescription_json(self):
        """ convert to a discoverydocument json"""
        pass

    def __hash__(self):
        return hash(self.name+self.version)