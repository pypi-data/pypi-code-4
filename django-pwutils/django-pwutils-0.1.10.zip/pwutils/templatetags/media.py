# -*- coding: utf-8 -*-
#getted from http://softwaremaniacs.org/blog/2009/03/22/media-tag/

import os
import urlparse

from django import template
from django.conf import settings
from django.contrib.sites.models import Site

register = template.Library()


def _absolute_url(url):
    if url.startswith('http://') or url.startswith('https://'):
        return url
    domain = Site.objects.get_current().domain
    return 'http://%s%s' % (domain, url)


def get_url(filename, flags, setting='MEDIA'):
    url = urlparse.urljoin(getattr(settings, setting + '_URL'), filename)
    if 'absolute' in flags:
        url = _absolute_url(url)
    if (filename.endswith('.css') or filename.endswith('.js')) and \
        'no-timestamp' not in flags or 'timestamp' in flags:
        fullname = os.path.join(getattr(settings, setting + '_ROOT'), filename)
        if os.path.exists(fullname):
            url += '?%d' % os.path.getmtime(fullname)
    return url


@register.simple_tag
def media(filename, flags=''):
    flags = set(f.strip() for f in flags.split(','))
    return get_url(filename, flags)


@register.simple_tag
def static(filename, flags=''):
    flags = set(f.strip() for f in flags.split(','))
    return get_url(filename, flags, setting='STATIC')
