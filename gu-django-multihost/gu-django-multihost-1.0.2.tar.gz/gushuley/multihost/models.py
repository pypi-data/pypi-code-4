from django.db import models
from django.contrib.sites.models import Site as DjangoSite
from . import is_database_driven_modules_urls, get_available_urls


if is_database_driven_modules_urls():
    class ModuleUrls(models.Model):
        module_urls = models.CharField(max_length=255, primary_key=True)

        def __unicode__(self):
            return u'%s' % self.module_urls


def get_module_urls_column(field_name):
    if is_database_driven_modules_urls():
        return models.ForeignKey(ModuleUrls, db_column=field_name)
    else:
        return models.CharField(max_length=255, blank=True, null=True, choices=get_available_urls(), db_column=field_name)


class Site(models.Model):
    site = models.ForeignKey(DjangoSite)
    host_regexp = models.CharField(max_length=255)
    urls_module = get_module_urls_column('urls_module')
    order = models.IntegerField(db_column="_order")

    def __unicode__(self):
        if self.site:
            return u'%s' % self.site

        return u'%s' % self.host_regexp

    class Meta:
        ordering = ['order']