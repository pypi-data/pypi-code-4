from hk2.types.annotations import ClassAnnotation

#===========================================================

class Service(ClassAnnotation):
    def apply(self, t, scope=None):
        self.scope = scope
