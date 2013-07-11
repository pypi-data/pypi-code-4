from resttouch.serializators import PlainText

__all__ = ('PathParam', 'QueryParam', 'BodyParam')


class Param(object):
    required = True
    
    def __init__(self, value, default=None):
        self.value = str(value)
        self.default = default

    def __str__(self, str):
        return str


class PathParam(Param):
    pass


class QueryParam(Param):
    def __init__(self, *args, **kwargs):
        self.required = kwargs.pop('required', True)
        super(QueryParam, self).__init__(*args, **kwargs)


class BodyParam(Param):
    def __init__(self, value='body', default=None, serializator=PlainText):
        self.serializator = serializator()
        self.value = value
        self.default = default

    def __str__(self, str):
        return self.serializator.serialize(str)