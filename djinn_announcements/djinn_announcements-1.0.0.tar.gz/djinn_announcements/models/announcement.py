from django.db import models
from django.utils.translation import ugettext_lazy as _
from djinn_contenttypes.registry import CTRegistry
from djinn_contenttypes.models.base import BaseContent
from djinn_announcements.settings import ANNOUNCEMENT_STATUS


class Announcement(BaseContent):

    text = models.TextField(_('Text'))
    status = models.IntegerField(_('Status'), blank=True, null=True) 
    priority = models.IntegerField(_("Priority"), default=0)

    @property
    def sorted_updates(self):

         return self.updates.order_by("-date")

    def __unicode__(self):

        return self.title

    @property
    def formatted_status(self):

        """ Format according to vocabulary """

        return ANNOUNCEMENT_STATUS.get(self.status, "")

    class Meta:
        app_label = 'djinn_announcements'
        ordering = ('-created', )


CTRegistry.register("announcement", 
                    {"class": Announcement,
                     "app": "djinn_announcements",
                     "label": _("Announcement"),
                     "global_add": False,
                     "add_permission": "djinn_announcements.add_announcement",
                     "filter_label": "",
                     "name_plural": _("announcements")})
