from tornado_extensions.cache import cache
from tornado_extensions.sessions.backends.base import SessionBase, CreateError
from tornado import gen


class SessionStore(SessionBase):
    """
    A cache-based session store.
    """

    prefix = 'p:'

    def __init__(self, *args, **kwargs):
        self._cache = cache
        super(SessionStore, self).__init__(*args, **kwargs)

    @property
    def cache_key(self):
        return self.prefix + self._get_or_create_session_key()

    @gen.engine
    def load(self, callback=None):
        self.loaded = True
        try:
            session_data = yield gen.Task(self._cache.get, self.cache_key, None)
            print session_data, "session data"
        except Exception:
            # Some backends (e.g. memcache) raise an exception on invalid
            # cache keys. If this happens, reset the session. See #17810.
            session_data = None
        if session_data is not None:
            self._session_cache = session_data
            if callback:
                callback(session_data)
            raise StopIteration
        self.create()
        if callback:
            self._session_cache = {}
            callback(self._session)

    def create(self):
        # Because a cache can fail silently (e.g. memcache), we don't know if
        # we are failing to create a new session because of a key collision or
        # because the cache is missing. So we try for a (large) number of times
        # and then raise an exception. That's the risk you shoulder if using
        # cache backing.
        for i in xrange(10000):
            self._session_key = self._get_new_session_key()
            try:
                yield gen.Task(self.save, must_create=True)
            except CreateError:
                continue
            self.modified = True
            return
        raise RuntimeError("Unable to create a new session key.")

    @gen.engine
    def save(self, must_create=False, callback=None):
        if must_create:
            func = self._cache.add
        else:
            func = self._cache.set
        result = yield gen.Task(func, self.cache_key,
                      self._get_session(),
                      self.get_expiry_age())
        if must_create and not result:
            raise CreateError
        if callback:
            callback(None)

    @gen.engine
    def exists(self, session_key, callback=None):
        result = yield gen.Task(self._cache.has_key, (self.prefix + session_key))
        if callback:
            callback(result)

    @gen.engine
    def delete(self, session_key=None, callback=None):
        if session_key is None:
            if self.session_key is None:
                if callback:
                    callback(None)
                raise StopIteration
            session_key = self.session_key
        yield gen.Task(self._cache.delete, (self.prefix + session_key))
        if callback:
            callback(None)
