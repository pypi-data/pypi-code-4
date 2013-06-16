from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


CACHE_TIME = getattr(settings, 'SWITTER_CACHE_TIME', 2 * 60)
CONSUMER_KEY = getattr(settings, 'SWITTER_CONSUMER_KEY', '')
CONSUMER_SECRET = getattr(settings, 'SWITTER_CONSUMER_SECRET', '')
ACCESS_TOKEN = getattr(settings, 'SWITTER_ACCESS_TOKEN', '')
ACCESS_TOKEN_SECRET = getattr(settings, 'SWITTER_ACCESS_TOKEN_SECRET', '')

if not CONSUMER_KEY or not CONSUMER_SECRET \
   or not ACCESS_TOKEN or not ACCESS_TOKEN_SECRET:
    raise ImproperlyConfigured('Twitter credentials are not set. Please specify ' +\
                               'SWITTER_CONSUMER_KEY, SWITTER_CONSUMER_SECRET, ' +\
                               'SWITTER_ACCESS_TOKEN and SWITTER_ACCESS_TOKEN_SECRET ' +\
                               'in your settings.')
