### -*- coding: utf-8 -*- ####################################################
from django.core.cache import cache

SESSION_GROUP_KEY = 'alphabetic_default_group'
DEFAULT_GROUP = 'rus'
CACHE_SECOND_PREFIX = 'alphabetic_second'

def get_group(request):
    return request.session.get(SESSION_GROUP_KEY, DEFAULT_GROUP)

def set_group(request, group_key):
    request.session[SESSION_GROUP_KEY] = group_key

def get_cache_key(queryset, letter, cache_params):
    """Generates unique cache key"""
    try:
        ident_class = queryset.model.__name__
    except AttributeError:
        ident_class = ''
    
    return "_".join([CACHE_SECOND_PREFIX, ident_class, letter]+list(cache_params))

    
def get_second_level(queryset, letter, cache_params):
    key = get_cache_key(queryset, letter, cache_params)
    if key:
        return cache.get(key)

def set_second_level(queryset, letter, second_level, timeout, cache_params):
    key = get_cache_key(queryset, letter, cache_params)
    if key:
        cache.set(key, second_level, timeout)
