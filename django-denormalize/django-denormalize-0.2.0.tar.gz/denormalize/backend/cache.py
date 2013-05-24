import time

from django.core import cache
from django.conf import settings

from .base import BackendBase

import logging
log = logging.getLogger(__name__)


class CacheBackend(BackendBase):
    """Backend that uses the Django cache API

    This is useful to speedup your Django application. This backend will
    try to find the requested document in the Django cache, and update the
    cache on a cache miss. Changes to the underlying data will be detected
    immediately, and the cache updated accordingly, so you do not have to
    worry about cache invalidation yourself.
    """

    cache_prefix = __name__
    cache_backend = 'default'
    # Long enough to do real caching, short enough to notice problems
    # during development
    cache_timeout = getattr(settings, 'DENORMALIZE_CACHE_TIMEOUT', 3600)

    # Log get_doc timings at the DEBUG level during development to find
    # performance bottlenecks. Fetching data from a memcached server
    # requires both a network roundtrip and unpickling the data, so it
    # might still be useful to add a short cache (say 5 seconds) in
    # local memory for often used documents.
    log_timings = getattr(settings, 'DEBUG', False)

    # Only used by get_doc_cached for an extra performance boost
    locmem_speedup_timeout = getattr(settings,
        'DENORMALIZE_CACHE_LOCMEM_SPEEDUP_TIMEOUT', 5)
    _locmem_speedup_cache = None

    # TODO: instead of updating a cache with a new doc, maybe just unset it
    #       and update it on the first access. Maybe make this behavior
    #       configurable

    def __init__(self, name="default", timeout=None):
        super(CacheBackend, self).__init__(name=name)
        self.cache = cache.get_cache(self.cache_backend)
        if timeout:
            self.cache_timeout = timeout
        self._locmem_speedup_cache = {}

    def _cache_key(self, collection, doc_id):
        return ':'.join((self.cache_prefix, collection.name, str(doc_id)))

    def deleted(self, collection, doc_id):
        log.debug('deleted: %s %s', collection.name, doc_id)
        key = self._cache_key(collection, doc_id)
        # We use an empty document to distinguish this from a cache miss
        self.cache.set(key, {}, self.cache_timeout)
        self._invalidate_locmem_speedup_cache(collection, doc_id)

    def added(self, collection, doc_id, doc):
        log.debug('added: %s %s', collection.name, doc_id)
        key = self._cache_key(collection, doc_id)
        self.cache.set(key, doc, self.cache_timeout)
        self._invalidate_locmem_speedup_cache(collection, doc_id)

    def changed(self, collection, doc_id, doc):
        log.debug('changed: %s %s', collection.name, doc_id)
        key = self._cache_key(collection, doc_id)
        self.cache.set(key, doc, self.cache_timeout)
        self._invalidate_locmem_speedup_cache(collection, doc_id)

    def get_doc(self, collection, doc_id):
        # In case it's passed by name, convert to the object
        collection = self._get_collection(collection)

        key = self._cache_key(collection, doc_id)
        log_timings = self.log_timings
        if log_timings: t0 = time.time()
        doc = self.cache.get(key, None)
        if log_timings: t1 = time.time()

        if doc is None:
            # Update cache
            if log_timings:
                ut0 = time.time()
            try:
                doc = collection.dump_id(doc_id)
            except collection.model.DoesNotExist:
                # Cache the fact that it does not exist
                self.deleted(collection, doc_id)
                return None

            self.added(collection, doc_id, doc)
            if log_timings:
                ut1 = time.time()
                udt = (ut1 - ut0) * 1000
                log.debug("Cache collection update for %s:%s took %.1f ms",
                    collection.name, doc_id, udt)
            return doc

        elif not doc:
            # Does not exist
            return None

        else:
            # Found it
            if log_timings:
                dt = (t1 - t0) * 1000
                log.debug("Cache get for %s:%s took %.1f ms",
                    collection.name, doc_id, dt)
            return doc

    def get_doc_cached(self, collection, doc_id, timeout=None):
        """Like get_doc(), but backed by an extra local memory cache layer.

        Fetching data from a memcached server requires both a network
        roundtrip and unpickling the data, so it can be useful to add
        a short cache in local memory for often used documents. This
        method does just that.

        Any updates done in the current process will immediately invalidate
        this local cache layer, but updates done by other processes/servers
        cannot be detected, so keep this cache time low. Using this will
        basically add latency to cache invalidation.

        The default timeout is 5 seconds and can be overridden in your
        settings, or by subclassing this backend, or by passing the timeout
        explicitly to this method. If you have 10 requests per second for
        a document, this will save you a memcached roundtrip and unpickle
        for 98% of your requests, at a cost of a 5 second delay in
        invalidation.
        """
        collection_name = collection if isinstance(collection, basestring) \
                          else collection.name

        col_cache = self._locmem_speedup_cache.setdefault(collection_name, {})
        cached = col_cache.get(doc_id, None)
        if cached is not None:
            ts, doc = cached
            timeout = timeout or self.locmem_speedup_timeout
            if ts + timeout >= time.time():
                # Cached value is still valid
                return doc

        # Update locmem speedup cache
        doc = self.get_doc(collection, doc_id)
        col_cache[doc_id] = time.time(), doc
        return doc

    def _invalidate_locmem_speedup_cache(self, collection, doc_id):
        # Invalidates any locmem speedup cache for given collection and doc_id,
        # so that the local process immediately sees changes made locally.
        try:
            col_cache = self._locmem_speedup_cache[collection.name]
        except KeyError:
            pass
        else:
            try:
                del col_cache[doc_id]
            except KeyError:
                pass

