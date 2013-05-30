from django.db import models
from cms.models.fields import PlaceholderField
from django.contrib.sites.models import Site


class Autoblock(models.Model):
    composite_id = models.CharField(max_length=150)
    content = PlaceholderField('content')
    site = models.ForeignKey(Site)

    def __unicode__(self):
        return self.composite_id
