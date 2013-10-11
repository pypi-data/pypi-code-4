class reify(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val
