# -*- coding: utf-8 -*-
import django.db.models.fields.related
import django.db.models
try:
    import idmapper.models
except:
    pass

class SubclasModelMixin(object):
    @classmethod
    def get_model_subclass_relations(cls):
        res = {}
        for name in dir(cls):
            try:
                attr = getattr(cls, name)
            except:
                attr = None
            if isinstance(attr, django.db.models.fields.related.SingleRelatedObjectDescriptor) and issubclass(attr.related.model, cls) and cls is not attr.related.model:
                res[name] = attr.related.model
        return res

    @classmethod
    def get_model_superclass_relations(cls):
        res = {}
        for name in dir(cls):
            try:
                attr = getattr(cls, name)
            except:
                attr = None
            if isinstance(attr, django.db.models.fields.related.ReverseSingleRelatedObjectDescriptor) and issubclass(cls, attr.field.rel.to) and cls is not attr.field.rel.to:
                res[name] = attr.field.rel.to
        return res

    @property
    def subclassobject(self):
        if hasattr(self, '_subclassobject'):
            return self._subclassobject
        for name in self.get_model_subclass_relations().iterkeys():
            # Use try around this since Django throws DoesNotExist instead of AttributeError... Bah!
            try:
                value = getattr(self, name, None)
            except:
                value = None
            if value is not None:
                self._subclassobject = value
                return value
        self._subclassobject = self
        return self

    @property
    def leafclassobject(self):
        while True:
            subclassobject = self.subclassobject
            if subclassobject is self:
                return self
            self = subclassobject
        
    @property
    def rootclassobject(self):
        while True:
            superclassobject = self.superclassobject
            if superclassobject is self:
                return self
            self = superclassobject
        

    @property
    def superclassobject(self):
        if hasattr(self, '_superclassobject'):
            return self._superclassobject
        for name in self.get_model_superclass_relations().iterkeys():
            # Use try around this since Django throws DoesNotExist instead of AttributeError... Bah!
            try:
                value = getattr(self, name)
            except:
                value = None
            if value is not None:
                self._superclassobject = value
                return value
        self._superclassobject = self
        return self

class MustBeOverriddenError(Exception):
    pass

def subclassproxy(fn):
    is_property = isinstance(fn, property)
    if is_property:
        fn = fn.fget

    name = fn.func_name

    def proxy(self, *arg, **kw):
        if self.subclassobject is self:
            try:
                return fn(self, *arg, **kw)
            except MustBeOverriddenError:
                try:
                    strrepr = unicode(self)
                except:
                    strrepr = id(self)
                raise NotImplementedError("%s.%s is a subclass proxy, but %s is not an instance of a subclass that overides it" % (type(self), name, strrepr))
        res = getattr(self.subclassobject, name)
        if not is_property:
            res = res(*arg, **kw)
        return res

    if is_property:
        proxy = property(proxy)
    return proxy
