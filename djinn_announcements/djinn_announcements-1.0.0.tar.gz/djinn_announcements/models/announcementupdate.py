from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djinn_contenttypes.models.base import FKContentMixin
from announcement import Announcement


class AnnouncementUpdate(models.Model, FKContentMixin):

    date = models.DateTimeField(_('Date'), default=datetime.now)
    text = models.TextField(_('Text'))
    announcement = models.ForeignKey(Announcement, related_name="updates")

    class Meta:
        app_label = 'djinn_announcements'
        ordering = ('date', )
