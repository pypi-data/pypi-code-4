from hk2.types import interface
from inject import inject

#===========================================================

@interface
class Activator(object):
    def getDependencies(self):
        """Returns list of inject_param
        :rtype : list(inject_param)"""

    def activate(self, dependencies):
        """Activates object with resolved dependencies"""

#===========================================================

class InstanceActivator(Activator):
    def __init__(self, inst):
        self.inst = inst

    def getDependencies(self):
        return []

    def activate(self, dependencies):
        return self.inst

#===========================================================

class ClassInitActivator(Activator):
    def __init__(self, clazz, ips):
        self.clazz = clazz
        self.ips = ips

    def getDependencies(self):
        return self.ips

    def activate(self, dependencies):
        return self.clazz(*dependencies)

#===========================================================

class ActivatorFactory(object):

    @staticmethod
    def getInstanceActivarot(inst):
        return InstanceActivator(inst)

    @staticmethod
    def getClassActivator(clazz):
        ips = inject.getParams(clazz.__init__)
        return ClassInitActivator(clazz, ips)
