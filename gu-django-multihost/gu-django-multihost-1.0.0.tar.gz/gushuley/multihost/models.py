from django.db import models
from django.contrib.sites.models import Site as DjangoSite


class Site(models.Model):
    site = models.ForeignKey(DjangoSite)
    host_regexp = models.CharField(max_length=255)
    urls_module = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(db_column="_order")

    def __unicode__(self):
        if self.site:
            return u'%s' % self.site

        return u'%s' % self.host_regexp

    class Meta:
        ordering = ['order']