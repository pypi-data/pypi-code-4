from zc.buildout.buildout import Options

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.port_base = int(options['base'])
        
        def get(key,default=None,seen=None):
            fallthrough = Options.get(options,key,default=None,seen=None)
            if fallthrough is not None:
                return fallthrough

            try:
                offset = int(key)
            except ValueError:
                offset = None
            
            if offset is not None:
                # Must always return strings
                return str(self.port_base + offset)
            
            return default

        options.get = get
        
    def install(self):
        return tuple()
    
    def update(self):
        pass
            