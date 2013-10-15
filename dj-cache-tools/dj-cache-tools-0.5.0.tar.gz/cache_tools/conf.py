from django.conf import settings

KEY_PREFIX = 'ct.obj'
CACHE_TIMEOUT = getattr(settings, 'CACHE_TIMEOUT', 10 * 60)
CACHE_ANCESTOR = getattr(settings, 'CACHE_ANCESTOR', True)