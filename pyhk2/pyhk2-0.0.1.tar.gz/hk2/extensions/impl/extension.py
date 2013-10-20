from hk2.extensions import IExtension

#===========================================================

class Extension(IExtension):
    def __init__(self):
        self._plugin = None
        self._pointName = None
        self._className = None
        self._params = {}
        self._point = None
    
    def plugin(self):
        return self._plugin
    
    def extensionPoint(self):
        return self._point
    
    def className(self):
        return self._className
    
    def parameters(self):
        return self._params