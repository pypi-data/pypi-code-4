from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from cachefly import Client


# Fetch the credentials.
api_key = getattr(settings, 'CACHEFLY_API_KEY', None)

if not api_key:
    raise ImproperlyConfigured('CACHEFLY_API_KEY is required.')

# Initialize the application-wide client.
client = Client(api_key)


__all__ = (
    'client',
)
