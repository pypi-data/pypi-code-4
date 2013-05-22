# -*- coding: utf8 -*-
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from memento import choices


class LogEntry(models.Model):
    message = models.TextField()
    content_type = models.ForeignKey(ContentType, related_name='log_entries', null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    severity = models.IntegerField(
        choices=getattr(settings, 'MEMENTO_SEVERITY_CHOICES', choices.SEVERITIES),
        default=getattr(settings, 'MEMENTO_SEVERITY_DEFAULT', 1)
    )
    last_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-last_timestamp',)

    @property
    def count(self):
        return self.events.all().count()

    @property
    def object_as_string(self):
        return str(self.content_object)

    def add_event(self):
        event = LogEvent.objects.create(entry=self)
        self.last_timestamp = event.timestamp
        self.save()


class LogEvent(models.Model):
    entry = models.ForeignKey(LogEntry, related_name='events', editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ( 'entry', '-timestamp')