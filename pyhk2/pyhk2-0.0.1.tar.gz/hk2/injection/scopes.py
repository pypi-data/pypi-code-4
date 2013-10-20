from hk2.types import interface

#===========================================================

@interface
class Scope(object):
    def get(self, binding, dependencies):
        """Instantiates binding with dependencies according to scope rules"""

#===========================================================

class NoScope(Scope):
    def get(self, binding, dependencies):
        return binding.activator.activate(dependencies)

#===========================================================

class SingletonScope(Scope):
    def __init__(self):
        self.inst = None

    def get(self, binding, dependencies):
        if self.inst is None:
            self.inst = binding.activator.activate(dependencies)
        return self.inst
