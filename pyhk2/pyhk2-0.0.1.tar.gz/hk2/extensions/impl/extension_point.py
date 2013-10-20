from hk2.extensions import IExtensionPoint

#===========================================================

class ExtensionPoint(IExtensionPoint):
    def __init__(self):
        self._plugin = None
        self._name = None
        self._interface = None
        self._params = {}
        self._extensions = []
    
    def plugin(self):
        return self._plugin
    
    def name(self):
        return self._name
    
    def fullName(self):
        return self._plugin.name() + "::" + self._name
    
    def parameters(self):
        return self._params
    
    def interfaceName(self):
        return self._interface
    
    def extensions(self):
        return self._extensions
