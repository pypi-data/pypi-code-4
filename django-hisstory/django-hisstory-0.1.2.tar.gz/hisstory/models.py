# coding: utf-8
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import AnonymousUser
from django.forms.models import model_to_dict
from django_globals import get_current_user
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField


class Record(models.Model):
    user_content_type = models.ForeignKey(ContentType, related_name='+', blank=True, null=True)
    user_id = models.PositiveIntegerField(blank=True, null=True)
    user = generic.GenericForeignKey('user_content_type', 'user_id')
    object_content_type = models.ForeignKey(ContentType, related_name='+')
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('object_content_type', 'object_id')
    create_date = models.DateTimeField(auto_now_add=True)
    data = JSONField()

    def _get_field_name(self, field):
        try:
            field_name = self.object._meta.get_field(field).verbose_name
        except models.FieldDoesNotExist:
            hisstory = getattr(self.object, 'Hisstory', None)
            if hisstory:
                hisstory = self.object.Hisstory()
            hisstory_field_names = getattr(hisstory, 'field_names', {})
            field_name = hisstory_field_names.get(field, field)
        return field_name

    def _get_simple_field_display(self, field):
        field_name = self._get_field_name(field)
        if not field in self.prev_data:
            self.display['added'].append(field_name)
        else:
            current = self.data[field] or ''
            prev = self.prev_data[field] or ''
            if not current == prev:
                self.display['changed'].append(field_name)

    def get_display(self):
        self.display = {'info': [], 'added': [], 'deleted': [], 'changed': []}

        try:
            ct = ContentType.objects.get_for_model(self.object)
            prev_record = self.get_previous_by_create_date(
                object_id=self.object.pk, object_content_type=ct)
        except Record.DoesNotExist:
            self.display['info'].append(_('Object created'))
            return self.display
        self.prev_data = prev_record.data

        for field in self.data:
            prev_field_data = self.prev_data.get(field, [])
            if type(self.data[field]) is list:
                if self.data[field] and type(self.data[field][0]) is dict:
                    self._get_simple_field_display(field)
                else:
                    added = list(set(self.data[field]) - set(prev_field_data))
                    deleted = list(set(prev_field_data) - set(self.data[field]))
                    self.display['added'] += added
                    self.display['deleted'] += deleted
            else:
                self._get_simple_field_display(field)
            if field in self.prev_data:
                self.prev_data.pop(field)

        for field in self.prev_data:
            field_name = self._get_field_name(field)
            self.display['deleted'].append(field_name)

        return self.display


    class Meta:
        ordering = ['-create_date', '-pk']


class HisstoryModel(models.Model):

    def save(self, *args, **kwargs):
        super(HisstoryModel, self).save(*args, **kwargs)
        self.create_record()

    def get_record_data(self):
        hisstory = self.__class__.Hisstory()
        data = model_to_dict(self, fields=hisstory.fields)
        additional_data = getattr(hisstory, 'get_additional_data', None)
        if additional_data:
            data.update(additional_data(self))
        return data

    def _get_previous_record_data(self):
        ct = ContentType.objects.get_for_model(self)
        prev_record = Record.objects.filter(
            object_id=self.pk, object_content_type=ct)
        if prev_record:
            return prev_record[0].data

    def create_record(self):
        record = Record()
        current_user = get_current_user()
        if not isinstance(current_user, AnonymousUser):
            record.user = current_user
        record.object = self
        record.data = self.get_record_data()
        if not record.data == self._get_previous_record_data():
            record.save()

    @property
    def model_name(self):
        return ContentType.objects.get_for_model(self).model

    @property
    def hisstory(self):
        ct = ContentType.objects.get_for_model(self)
        records = Record.objects.filter(object_id=self.pk, object_content_type=ct)
        history = []
        for record in records:
            display = record.get_display()
            if display['added']:
                history.append({
                    'date': record.create_date,
                    'user': record.user,
                    'comment': _('Added {}').format(', '.join(map(unicode, display['added']))),
                })
            if display['deleted']:
                history.append({
                    'date': record.create_date,
                    'user': record.user,
                    'comment': _('Removed {}').format(', '.join(map(unicode, display['deleted']))),
                })
            if display['changed']:
                history.append({
                    'date': record.create_date,
                    'user': record.user,
                    'comment': _('Changed {}').format(', '.join(map(unicode, display['changed']))),
                })
            if display['info']:
                history.append({
                    'date': record.create_date,
                    'user': record.user,
                    'comment': u'. '.join(map(unicode, display['info'])),
                })
        return history


    class Meta:
        abstract = True
