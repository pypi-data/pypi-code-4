#-*- coding:utf-8 -*-
import logging

from django.db import models

from domains.models import Domain

logger = logging.getLogger(__name__)


class NotificationLog(models.Model):
    SMS = 'SMS'
    NOTIFICATION_KIND_CHOICES = (
        (SMS, 'SMS'),
    )

    domain = models.ForeignKey(Domain)
    kind = models.TextField(max_length=3, choices=NOTIFICATION_KIND_CHOICES, null=True, blank=True, default=SMS)
    created = models.DateTimeField(auto_now_add=True)
