# -*- coding: utf-8 -*-

from urlparse import urljoin

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch
from pwutils.utils import get_current_site_url

register = template.Library()


@register.simple_tag
def external_url(url, extra1=None, extra2=None):

    if url.startswith('http://') or url.startswith('https://'):
        return url
    domain = get_current_site_url()

    args = []  # XXX use URL template tag here
    if extra1 is not None:
        args.append(extra1)
    if extra2 is not None:
        args.append(extra2)

    try:
        url = reverse(url, args=args)
    except NoReverseMatch:
        pass

    return urljoin(domain, url)
