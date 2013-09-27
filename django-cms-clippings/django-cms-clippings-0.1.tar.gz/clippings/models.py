from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from cms.models.fields import PlaceholderField


class Clipping(models.Model):

    """Clipping maps a placeholder to a name that is unique for a given site.

    """

    identifier = models.CharField(max_length=40, db_index=True)
    site = models.ForeignKey(Site, null=True)
    content = PlaceholderField('content')

    class Meta:
        unique_together = (("identifier", "site"),)

    identifier.verbose_name = _("identifier")
    site.verbose_name = _("site")
    content.verbose_name = _("content")

    identifier.help_text = _("The name used to find and display this clipping")
    site.help_text = _("The web site where this clipping will be displayed")

    def __unicode__(self):
        return self.identifier
