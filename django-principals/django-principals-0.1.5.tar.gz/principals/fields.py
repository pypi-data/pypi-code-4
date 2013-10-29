import datetime
import warnings

from django.db import models
from django.db.models.signals import post_delete, post_save, pre_delete
from django.db.models import Q

try:
    from django.utils.timezone import now
except ImportError:
    now = datetime.datetime.now


class PrincipalField(models.BooleanField):
    def __init__(self, verbose_name=None, name=None, default=False, collection=None, parent_link=None, *args, **kwargs):
        # we have extended 'unique' needs so disallow 'unique'
        if 'unique' in kwargs:
            raise TypeError("%s can't have a unique constraint." % self.__class__.__name__)
        super(PrincipalField, self).__init__(verbose_name, name, default=default, *args, **kwargs)
        # we need collection to be a list so if it's a string, create a list accordingly
        if isinstance(collection, basestring):
            collection = (collection,)
        self.collection = collection
        self.parent_link = parent_link
        self._collection_changed = None

    def contribute_to_class(self, cls, name):
        super(PrincipalField, self).contribute_to_class(cls, name)
        # disallow 'unique_together'
        for constraint in cls._meta.unique_together:
            if self.name in constraint:
                raise TypeError("%s can't be part of a unique constraint." % self.__class__.__name__)
        self.auto_now_fields = []
        for field in cls._meta.fields:
            if getattr(field, 'auto_now', False):
                self.auto_now_fields.append(field)
        setattr(cls, self.name, self)
        post_save.connect(self.update_on_save, sender=cls)

    def get_internal_type(self):
        return 'BooleanField'

    def pre_save(self, model_instance, add):
        # check if the node has been moved to another collection
        # if it has, delete it from the old collection.
        previous_instance = None
        collection_changed = False
        if not add and self.collection is not None:
            previous_instance = type(model_instance)._default_manager.get(pk=model_instance.pk)
            for field_name in self.collection:
                field = model_instance._meta.get_field(field_name)
                current_field_value = getattr(model_instance, field.attname)
                previous_field_value = getattr(previous_instance, field.attname)
                if previous_field_value != current_field_value:
                    collection_changed = True
                    break
        if not collection_changed:
            previous_instance = None
        self._collection_changed = collection_changed
        if collection_changed:
            self.remove_from_collection(previous_instance)
        cache_name = self.get_cache_name()
        current, updated = getattr(model_instance, cache_name)
        if collection_changed:
            current = None
        if add:
            if updated is None:
                updated = current
            current = None

        # existing instance & principal not modified - no cleanup required
        if current is not None and updated is None:
            return current

        # instance inserted; cleanup required on post_save
        setattr(model_instance, cache_name, (current, updated))
        return updated

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError("%s must be accessed via instance." % self.name)
        try:
            current, updated = getattr(instance, self.get_cache_name())
        except AttributeError:
            return self.default
        return current if updated is None else updated

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("%s must be accessed via instance." % self.name)
        if value is None:
            value = self.default
        cache_name = self.get_cache_name()
        try:
            current, updated = getattr(instance, cache_name)
        except AttributeError:
            current, updated = value, None
        else:
            updated = value
        setattr(instance, cache_name, (current, updated))

    def get_collection(self, instance):
        filters = {}
        if self.collection is not None:
            for field_name in self.collection:
                field = instance._meta.get_field(field_name)
                field_value = getattr(instance, field.attname)
                if field.null and field_value is None:
                    filters['%s__isnull' % field.name] = True
                else:
                    filters[field.name] = field_value
        model_cls = type(instance)
        parent_link = self.parent_link
        if parent_link is not None:
            model = model_cls._meta.get_field(parent_link).rel.to
        return model_cls._default_manager.filter(**filters)

    def remove_from_collection(self, instance):
        """
        Removes an item from the collection.
        """
        queryset = self.get_collection(instance).exclude(pk=instance.pk)
        current = getattr(instance, self.get_cache_name())[0]
        updates = {self.name: models.F(self.name) }
        if self.auto_now_fields:
            right_now = now()
            for field in self.auto_now_fields:
                updates[field.name] = right_now
        queryset.update(**updates)

    def update_on_save(self, sender, instance, created, **kwargs):
        cache_name = self.get_cache_name()
        try:
            current, updated = getattr(instance, cache_name)
        except:
            current, updated = None, getattr(instance, self.name)

        need_updating = updated is True and current is not True

        # Quit early if nothing changed
        if not need_updating:
            return

        Model = type(instance)
        queryset = Model._default_manager
        queryset = self.get_collection(instance)
        queryset = queryset.exclude(pk=instance.pk).filter(**{self.name: True})
        if not self.collection is None:
            for field_name in self.collection:
                queryset = queryset.filter(**{field_name: getattr(instance, field_name)})

        # Un-feature any records currently featured
        queryset.update(**{self.name: False})

        setattr(instance, cache_name, (updated, updated))

    def south_field_triple(self):
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.BooleanField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

