from tornado_extensions.cache.backends.base import CacheBase
import tornadoasyncmemcache as memcache
from tornado import gen


class MemcachedCache(CacheBase):
    def __init__(self, server, params=None):
        super(MemcachedCache, self).__init__(params or {})
        if isinstance(server, basestring):
            self._servers = server.split(';')
        else:
            self._servers = server

    @property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            self._client = memcache.ClientPool(self._servers, maxclients=100)
        return self._client

    @gen.engine
    def add(self, key, value, timeout=0, version=None, callback=None):
        key = self.make_key(key, version=version)
        result = yield gen.Task(self._cache.add, key, value)
        callback(result)

    @gen.engine
    def get(self, key, default=None, version=None, callback=None):
        key = self.make_key(key, version=version)
        val = yield gen.Task(self._cache.get, key)
        if val is None:
            val = default
        callback(val)

    @gen.engine
    def set(self, key, value, timeout=0, version=None, callback=None):
        key = self.make_key(key, version=version)
        result = yield gen.Task(self._cache.set, key, value)
        callback(result)

    @gen.engine
    def delete(self, key, version=None, callback=None):
        key = self.make_key(key, version=version)
        result = yield gen.Task(self._cache.delete, key)
        callback(result)
