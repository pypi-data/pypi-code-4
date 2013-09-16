from django.conf import settings
from django.db import models

if 'cms' in settings.INSTALLED_APPS:
    from cms.models import CMSPlugin

    class SignupFormPlugin(CMSPlugin):
        list_id = models.CharField(max_length=30)

        def __unicode__(self):
            return self.list_id
