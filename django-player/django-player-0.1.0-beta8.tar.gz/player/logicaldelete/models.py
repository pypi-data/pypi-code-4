from datetime import datetime
from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _


class LogicalDeletedManager(models.Manager):

    def get_query_set(self):
        if self.model:
            return super(LogicalDeletedManager, self).get_query_set().filter(is_deleted=False)

    def with_deleted(self):
        if self.model:
            return super(LogicalDeletedManager, self).get_query_set()

    def only_deleted(self):
        if self.model:
            return super(LogicalDeletedManager, self).get_query_set().filter(is_deleted=True)

    def get(self, *args, **kwargs):
        ''' if a specific record was requested, return it even if it's deleted '''
        return self.with_deleted().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        ''' if pk was specified as a kwarg, return even if it's deleted '''
        if 'pk' in kwargs or 'id' in kwargs:
            return self.with_deleted().filter(*args, **kwargs)
        return self.get_query_set().filter(*args, **kwargs)


class Model(models.Model):
    date_deleted = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(_('is deleted'), default=False)

    objects = LogicalDeletedManager()

    def delete(self, using=None, purge=False):
        if not purge:
            signals.pre_delete.send(sender=self.__class__, instance=self)
            self.date_deleted = datetime.now()
            self.is_deleted = True
            self.save(using=using)
        else:  # we remove object
            super(Model, self).delete(using=using)

    class Meta:
        abstract = True
