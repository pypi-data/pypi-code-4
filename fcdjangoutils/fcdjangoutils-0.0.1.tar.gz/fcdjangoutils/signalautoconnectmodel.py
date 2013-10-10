# -*- coding: utf-8 -*-
import django.db.models
try:
    import idmapper.models
except:
    idmapper = None

def autoconnect(cls):
    if not hasattr(cls, 'Meta') or not getattr(cls.Meta, 'abstract', False):
        for signame in ("pre_save", "post_save", "pre_delete", "post_delete", "pre_init", "post_init"):
            if hasattr(cls, 'on_'+signame):
                getattr(django.db.models.signals, signame).connect(getattr(cls, 'on_'+signame), sender=cls)
        for key in dir(cls):
            try:
                value = getattr(cls, key)
            except:
                pass
            else:
                if isinstance(value, (django.db.models.fields.related.ReverseManyRelatedObjectsDescriptor, django.db.models.fields.related.ManyRelatedObjectsDescriptor)):
                    if hasattr(cls, 'on_m2m_changed_for_'+key):
                        getattr(django.db.models.signals, 'm2m_changed').connect(getattr(cls, 'on_m2m_changed_for_'+key), sender=value.through)
   

class SignalAutoConnectModel(django.db.models.Model):
    class __metaclass__(django.db.models.Model.__metaclass__):
        def __init__(cls, *arg, **kw):
            django.db.models.Model.__metaclass__.__init__(cls, *arg, **kw)
            autoconnect(cls)
    class Meta:
        abstract = True


if idmapper is not None:
    class SharedMemorySignalAutoConnectModel(idmapper.models.SharedMemoryModel):
        class __metaclass__(idmapper.models.SharedMemoryModel.__metaclass__):
            def __init__(cls, *arg, **kw):
                idmapper.models.SharedMemoryModel.__metaclass__.__init__(cls, *arg, **kw)
                autoconnect(cls)
        class Meta:
            abstract = True

