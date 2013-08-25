class json_field(object):
    def __init__(self, name, default=None, ser_if_null=True):
        self._name = name
        self._default = default 
        self._ser_if_null = ser_if_null
        self._value = None

    def __get__(self, obj, objtype=None):
        return self._value or self._default
       
    def __set__(self, obj, val):
		self._value = val
