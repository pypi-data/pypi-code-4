from django.db.models import Manager
from django.db.models.query import QuerySet
from django.db.models.signals import post_save

from principals.fields import PrincipalField


class PrincipalQuerySet(QuerySet):
    def __init__(self, model=None, query=None, using=None, principal_field_name='principal'):
        super(PrincipalQuerySet, self).__init__(model, query, using)
        self.principal_field_name = principal_field_name

    def _clone(self, *args, **kwargs):
        queryset = super(PrincipalQuerySet, self)._clone(*args, **kwargs)
        queryset.principal_field_name = self.principal_field_name
        return queryset

    def set_principal(self, save=True):
        principal_field = self.model._meta.get_field_by_name(self.principal_field_name)[0]
        post_save.disconnect(principal_field.update_on_save, sender=self.model)
        for obj in self.iterator():
            setattr(obj, self.principal_field_name, False)
            if save:
                obj.save()
        post_save.connect(principal_field.update_on_save, sender=self.model)
        return self


class PrincipalManager(Manager):
    def __init__(self, principal_field_name='principal'):
        super(PrincipalManager, self).__init__()
        self.principal_field_name = principal_field_name

    def get_query_set(self):
        return PrincipalQuerySet(self.model, principal_field_name=self.principal_field_name)

    def set_principal(self):
        return self.get_query_set().set_principal()
