class json_property(object):
    def __init__(self, prefix=None, ser_if_null=True):
        self.prefix = prefix
        self._ser_if_null = ser_if_null

    def __call__(self, f):
        self.f = f
        if not self.prefix:
            self.prefix = f.__name__
        return self

    def __get__(self, obj, objtype=None):
        return self.f(obj)
       
