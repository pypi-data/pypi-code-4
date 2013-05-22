# -*- coding: utf8 -*-
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from memento.models import LogEntry


class Logger(object):

    @staticmethod
    def log(message, obj=None, severity=None):
        """
        Adds a log entry and an event related to that log entry.

        :param message: a string
        :param obj: a model, optional
        :param severity: a integer, optional

        :type message str
        :type obj object
        :type severity int
        """
        if severity is None:
            severity = getattr(settings, 'MEMENTO_SEVERITY_DEFAULT', 1)
        if not obj is None:
            entry = LogEntry.objects.get_or_create(
                message=message,
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
                severity=severity
            )
        else:
            entry = LogEntry.objects.get_or_create(
                message=message,
                severity=severity
            )

        entry[0].add_event()

    @staticmethod
    def get_log_entry(obj):
        """
        Get log entries related to object

        :param obj: a model, optional
        :param severity: a integer, optional

        :type obj object
        :type severity int
        """

        return LogEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id
        )
