import types

from inspect import isclass, isfunction, ismethod

from .fields import build_field

class SimpleModelType(type):
    def __new__(mcs, class_name, bases, attrs_dict):
        field_names = []
        for base in bases:
            if isinstance(base, mcs):
                field_names.extend(base._simple_model_field_names)

        fields_dict = attrs_dict

        fields_class = attrs_dict.get('Fields')
        if isclass(fields_class):
            fields_dict = fields_class.__dict__

        for name, value in fields_dict.iteritems():
            if not (name.startswith('__') or
                    isfunction(value) or
                    ismethod(value)):
                field = build_field(value)
                field_names.append(name)
                attrs_dict[name] = field

        attrs_dict['_simple_model_field_names'] = field_names
        return type.__new__(mcs, class_name, bases, attrs_dict)


class SimpleModel(object):
    __metaclass__ = SimpleModelType

    def __init__(self, attrs=None, **other_attrs):
        attrs = dict(attrs or {})
        attrs.update(other_attrs)

        for name in self._simple_model_field_names:
            if name in attrs:
                setattr(self, name, attrs[name])

    def __iter__(self):
        return ((name, getattr(self, name))
                for name in self._simple_model_field_names)

    def __repr__(self):
        attrs_repr = ', '.join('%s=%r' % item for item in self)
        return '%s(%s)' % (self.__class__.__name__, attrs_repr)


if __name__ == '__main__':
    class ChildModel(SimpleModel):
        id = int

    class TestModel(SimpleModel):
        basic = int
        basic_default = 1
        any_list = []
        int_list = [int]
        str_bool_dict = {str: bool}
        child = ChildModel
