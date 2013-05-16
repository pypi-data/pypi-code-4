from logging import getLogger

import time

from django.conf import settings

from django.db import models
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.http import urlquote




log = getLogger('dprofiling.models')


def upload_profile(instance, filename):
    return '%s/%s/%s' % (instance.session.site.pk,
            urlquote(instance.session.path.replace('/','_')).strip('_'),
            time.time(),)

class Session(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    path = models.CharField(max_length=200, null=False, blank=False, db_index=True)
    site = models.ForeignKey(Site, null=False, blank=False, db_index=True)
    active = models.BooleanField(default=False, null=False, blank=False,
            db_index=True)


    objects = models.Manager()
    on_site = CurrentSiteManager()

    def __unicode__(self):
        return self.name

class Profile(models.Model):
    session = models.ForeignKey(Session, null=False, blank=False,
            db_index=True, related_name='profiles')
    dump = models.FileField(null=False, blank=False, max_length=255,
            upload_to=getattr(settings, 'PROFILING_PROFILE_UPLOAD_TO', upload_profile),
            storage=getattr(settings, 'PROFILING_PROFILE_STORAGE', None))

from dprofiling import signals
