import copy
import types
import weakref

from inspect import isclass


def type_cast(value, type_):
    if type_ and not isinstance(value, type_):
        value = type_(value)
    return value


class Self(object): pass


class Field(object):
    default = None

    def __init__(self, example):
        self.data = weakref.WeakKeyDictionary()
        if example is None:
            self.field_type = None
        elif isclass(example):
            self.field_type = example
        else:
            self.default = example
            self.field_type = type(example)

    def type_cast(self, value):
        return type_cast(value, self.field_type)

    def __get__(self, instance, _):
        if instance not in self.data:
            self.data[instance] = copy.deepcopy(self.default)
        return self.data[instance]

    def __set__(self, instance, value):
        if self.field_type is Self:
            self.field_type = type(instance)
        self.data[instance] = self.type_cast(value)


class ListField(Field):
    default = []

    def __init__(self, item_type):
        if item_type == '__self__':
            item_type = None
        elif not isclass(item_type):
            raise ValueError('item_type must be a class')
        super(ListField, self).__init__(list)
        self.item_type = item_type

    def type_cast(self, values):
        return [type_cast(item, self.item_type) for item in values]

    def __set__(self, instance, value):
        if self.item_type is Self:
            self.item_type = type(instance)
        super(ListField, self).__set__(instance, value)

        
class DictField(Field):
    default = {}

    def __init__(self, key_type, value_type):
        if not isclass(key_type):
            raise ValueError('key_type must be a class')
        if value_type is not None and not isclass(value_type):
            raise ValueError('value_type must be a class')
        super(DictField, self).__init__(dict)
        self.key_type = key_type
        self.value_type = value_type

    def type_cast(self, dct):
        return {type_cast(k, self.key_type): type_cast(v, self.value_type)
                for k, v in dct.iteritems()}

    def __set__(self, instance, value):
        if self.key_type is Self:
            self.key_type = type(instance)
        if self.value_type is Self:
            self.value_type = type(instance)
        super(DictField, self).__set__(instance, value)

        
def build_field(example):
    if isinstance(example, Field):
        return example

    if example == Self:
        return SelfField()

    if isinstance(example, list) and len(example) == 1:
        item = example[0]
        if isclass(item):
            return ListField(item)

    if isinstance(example, dict) and len(example) == 1:
        key, value = example.iteritems().next()
        if isclass(key) and isclass(value):
            return DictField(key, value)

    return Field(example)
