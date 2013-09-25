# coding: utf-8
from collections import OrderedDict
from django.db.models import Model


__CONTENT_TYPES__ = OrderedDict()


class ContentType(object):

    def __init__(self, cls, verbose_name, objects=None):
        self.cls = cls
        self.verbose_name = verbose_name
        self._objects = objects

    @property
    def objects(self):
        if hasattr(self._objects, "__call__"):
            return self._objects()
        elif self._objects is not None:
            return self._objects
        return None

    def get_object(self, pk=None):
        if issubclass(self.cls, Model):
            return self.objects.get(pk=pk)
        return self.cls


def register(content_type, verbose_name=None, objects=None):
    if verbose_name is None:
        if issubclass(content_type, Model):
            verbose_name = content_type._meta.verbose_name.title()
        elif hasattr(content_type, "verbose_name"):
            if hasattr(content_type.verbose_name, "__call__"):
                verbose_name = content_type.verbose_name().title()
            else:
                verbose_name = content_type.verbose_name.title()
        else:
            verbose_name = content_type.__name__
    __CONTENT_TYPES__[repr(content_type)] = ContentType(content_type, verbose_name, objects)


def unregister(content_type):
    if repr(content_type) in __CONTENT_TYPES__:
        del __CONTENT_TYPES__[repr(content_type)]


def register_all(*content_types):
    for content_type in content_types:
        register(content_type)


def unregister_all(*content_types):
    global __CONTENT_TYPES__
    if len(content_types) == 0:
        __CONTENT_TYPES__ = OrderedDict()
    else:
        for content_type in content_types:
            unregister(content_type)


def content_types_choices():
    choices = [(k, v.verbose_name) for k, v in __CONTENT_TYPES__.items()]
    return choices


def objects_choices(content_type):
    if content_type not in __CONTENT_TYPES__:
        raise IndexError
    ct = __CONTENT_TYPES__[content_type]
    objects = ct.objects
    if objects is None:
        return [(-1, u"'{}' hasn't objects".format(ct.verbose_name))]
    return ((ob.pk, unicode(ob)) for ob in objects)


def get_object(content_type, pk=None):
    return __CONTENT_TYPES__[content_type].get_object(pk)
