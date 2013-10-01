# coding: utf-8
from django.conf import settings as django_settings


settings = {
    'REDIS_CACHE_SIZE': 5,
    'REDIS_PREFIX': 'django-search-statistic',
    'REDIS_SETTINGS': {
        'db': 1
    },
    'REMOVE_ON_STATUS': [400, 403, 404, 405],
    'default_query_confirm': False,
}
settings.update(
    getattr(django_settings, 'SEARCH_STATISTIC', {})
)

cache = None
try:
    import redis
    cache = redis.Redis(**settings['REDIS_SETTINGS'])
except ImportError:
    pass


def cache_key(key):
    return '{}::{}'.format(settings['REDIS_PREFIX'], key)
