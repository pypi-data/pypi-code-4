# -*- coding: utf-8 -*-
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.template import defaultfilters
from django.utils.cache import get_cache_key


def slugify(value):
    value = value.replace(u"æ", 'ae')
    value = value.replace(u"ø", 'o')
    value = value.replace(u"å", 'aa')
    return defaultfilters.slugify(value)

def unslugify(value):
    value = value.replace('-', ' ')
    value = ''.join([value[0].upper(), value[1:]])
    return value

def expire_page_cache(view, args=None):
    """
    Removes cache created by cache_page functionality.
    Parameters are used as they are in reverse()
    """

    if args is None:
        path = reverse(view)
    else:
        path = reverse(view, args=args)

    request = HttpRequest()
    request.path = path
    key = get_cache_key(request)
    if cache.has_key(key):
        cache.delete(key)