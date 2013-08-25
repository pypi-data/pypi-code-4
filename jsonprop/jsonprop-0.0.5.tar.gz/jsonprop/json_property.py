class json_property(object):
    def __init__(self, name=None, ser_if_null=True):
        self._name = name 
        self._ser_if_null = ser_if_null

    def __call__(self, f):
        self.f = f
        if not self._name:
            self._name = f.__name__
        return self

    def __get__(self, obj, objtype=None):
        return self.f(obj)
       
