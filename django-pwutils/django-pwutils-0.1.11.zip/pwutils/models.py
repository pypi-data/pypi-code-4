# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.files import ImageFieldFile

from pwutils.middleware import threadlocals

from pwutils.fields import ModificationDateTimeField, CreationDateTimeField, \
    DeletionDateTimeField, SouthFilePathField, datetime_now


class TimeStampedModel(models.Model):
    """ TimeStampedModel
    An abstract base class model that provides self-managed "created" and
    "modified" and 'deleted' fields.
    """
    created_date = CreationDateTimeField(verbose_name=u'Дата создания')

    modified_date = ModificationDateTimeField(verbose_name=u'Дата модификации')

    deleted_date = DeletionDateTimeField(verbose_name=u'Дата удаления',
                                         null=True, blank=True,
                                         editable=False)

    class Meta:
        abstract = True

    def _set_deleted(self, delete=True):
        if delete:
            date = datetime_now()
            self.deleted_date = date
        else:
            self._set_active()

    def _is_deleted(self):
        return self.deleted_date is not None

    def _set_active(self):
        self.deleted_date = None

    deleted = property(_is_deleted, _set_deleted)


class TimeStampedByUserModel(TimeStampedModel):

    created_by = models.ForeignKey(User, verbose_name=u'Создан кем',
                     related_name="%(app_label)s_%(class)s_created",
                     editable=False, null=True, blank=True)

    modified_by = models.ForeignKey(User, verbose_name=u'Редактировался кем',
                      related_name="%(app_label)s_%(class)s_modified",
                      editable=False, null=True, blank=True)

    deleted_by = models.ForeignKey(User, verbose_name=u'Удален кем',
                    related_name="%(app_label)s_%(class)s_deleted",
                    editable=False,
                    null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # If the object already existed, it will already have an id
        if self.id:
            # This object is being edited, not saved, set last_edited_by
            self.modified_by = threadlocals.get_current_user()
        else:
            # This is a new object, set the owner
            user = threadlocals.get_current_user()
            self.created_by = self.modified_by = user
        super(TimeStampedByUserModel, self).save()

    def _set_deleted(self, delete=True):

        if delete:
            self.deleted_by = threadlocals.get_current_user()
            super(TimeStampedByUserModel, self)._set_deleted(delete=delete)
        else:
            self._set_active()

    def _set_active(self):
        super(TimeStampedByUserModel, self)._set_active()
        self.deleted_by = None

    deleted = property(TimeStampedModel._is_deleted, _set_deleted)


class ModerationModel(models.Model):

    is_approved = models.BooleanField(u'Принято', default=False)
    approved = models.DateTimeField(u'Дата модерации',
                                    default=None, null=True, blank=True)

    class Meta:
        abstract = True


class PublicModel(models.Model):

    is_public = models.BooleanField(u'Опубликовано', default=False)
    published = models.DateTimeField(u'Дата публикации',
                                     default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        now = datetime_now()
        if self.is_public and self.published is None:
            self.published = now
        elif self.published is not None and self.published < now:
            self.is_public = True
        super(PublicModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class Measure(models.Model):

    title = models.TextField(verbose_name=u'Название', max_length=200)

    def __unicode__(self):
        return unicode(self.title)

    class Meta:
        verbose_name = u'Единица измерения'
        verbose_name_plural = u'Единицы измерения'

    @classmethod
    def default_value(cls):
        return cls.objects.get_or_create(title=u'услуга')[0]


class pwImageFieldFile(ImageFieldFile):

    def _get_rel_path(self):
        rel_path = self.field.storage.rel_path(self.name)
        return rel_path
    rel_path = property(_get_rel_path)


class pwImageField(models.ImageField):
    attr_class = pwImageFieldFile
