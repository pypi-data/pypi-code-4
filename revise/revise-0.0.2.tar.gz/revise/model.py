from revise.types import BaseType
from revise import errors
from collections import OrderedDict
import itertools

# Import
# -> Require & Coerce
# -> Validate
# -> Transform


class FieldDescriptor(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, resource, objtype):
        field = resource.fields.get(self.name)
        if not field:
            raise AttributeError(self.name)
        return resource.data.get(self.name) or field.default

    def __set__(self, resource, value):
        field = resource.fields.get(self.name)
        if not field:
            raise AttributeError(self.name)
        resource._clean()
        field._clean()
        resource.data[self.name] = value


class ModelMeta(type):

    def __new__(cls, name, bases, attrs):
        klass = super(ModelMeta, cls).__new__(cls, name, bases, attrs)
        fields = OrderedDict()
        f = ([(k, v) for (k, v) in attrs.items() if isinstance(v, BaseType)])
        for key, field in f:
            if not field.name:
                field.name = key
            fields[field.name] = field
            descriptor = FieldDescriptor(field.name)
            setattr(klass, field.name, descriptor)
        setattr(klass, '_fields', fields)
        return klass


class Model(object):

    # Reserved Words?
    # Raise Exception vs Dict Errors

    def __init__(self, data=None):
        self._clean()
        self._data = {}

        for field in self.fields.values():
            setattr(field, 'model', self)
            v = data.get(field.name, field.default)
            setattr(self, field.name, v)

    def validate(self):
        return not bool(self.errors)

    @property
    def errors(self):
        if not self._errors:
            for field in self.fields.values():
                field.validate(getattr(self, field.name))
                if field.errors:
                    map(self._errors.append, [e.dict for e in field.errors])
            self._validated = True
        return self._errors

    @property
    def fields(self):
        return self._fields

    @property
    def data(self):
        return self._data

    def _clean(self):
        self._validated = False
        self._errors = []

    __metaclass__ = ModelMeta
