# -*- coding: utf8 -*-

__all__=['behave_as', 'can_substitute', 'subtypeof']

def behave_as(*bases):
    dynamic_bases = __load_bases(bases)

    class Liskov(type):
        def __new__(cls, name, bases, attrs):
            return type.__new__(cls, name, dynamic_bases + bases, attrs)

    return Liskov

def subtypeof(base):
    mod_name, sep, cls_name = base.rpartition('.')
    module = __import__(mod_name, globals(), locals(), [cls_name])
    return getattr(module, cls_name, object)


def can_substitute(*bases):
    dynamic_bases = __load_bases(bases)

    def liskov(cls):
        bases = (cls, ) + dynamic_bases + cls.__bases__
        attrs = dict(cls.__dict__)
        return type(cls.__name__, bases, attrs)

    return liskov

def __load_bases(bases):
    dynamic_bases = tuple()
    for base in bases:
        cls = subtypeof(base)
        if cls not in dynamic_bases:
            dynamic_bases+= (cls, )
    return dynamic_bases

