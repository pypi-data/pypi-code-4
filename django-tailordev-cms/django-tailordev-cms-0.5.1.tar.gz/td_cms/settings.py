# -*- coding: utf-8 -*-
from django.conf import settings


# Disqus
DISQUS_SHORTNAME = getattr(settings,
                           'TD_CMS_DISQUS_SHORTNAME',
                           None)
