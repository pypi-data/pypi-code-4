"""
django_casscache
~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Matt Robenolt.
:license: BSD, see LICENSE for more details.
"""

from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.cache.backends.memcached import BaseMemcachedCache

try:
    import casscache
except ImportError:
    raise InvalidCacheBackendError('Could not import casscache')

__all__ = ['CasscacheCache']


class CasscacheCache(BaseMemcachedCache):
    "An implementation of a cache binding using casscache"
    def __init__(self, server, params):
        super(CasscacheCache, self).__init__(server, params,
                                             library=casscache,
                                             value_not_found_exception=ValueError)

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            self._client = self._lib.Client(self._servers, **self._options)
        return self._client

    def _get_memcache_timeout(self, timeout):
        """
        Cassandra deals with timeouts slightly different than Memcached.
        There is no limit on long timeouts.
        """
        if timeout is None:
            timeout = self.default_timeout
        return int(timeout)

    def close(self, **kwargs):
        # Lol, Django wants to close the connection after every request.
        # This is 100% not needed for Cassandra.
        pass


def noop_make_key(key, *args, **kwargs):
    """
    For use with KEY_FUNCTION, to not alter the key name at all.
    """
    return key
