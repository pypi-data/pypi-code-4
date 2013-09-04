"""A cache backend base implementations

"""
from tornado import gen
from game_commons.patterns import Singleton


def default_key_func(key, key_prefix, version):
    """
    Default function to generate keys.

    Constructs the key used by all other methods. By default it prepends
    the `key_prefix'. KEY_FUNCTION can be used to specify an alternate
    function with custom key making behavior.
    """
    return ':'.join([key_prefix, str(version), key.encode('utf-8')])


class CacheBase(object):
    __metaclass__ = Singleton

    version = 1
    key_prefix = ''

    def __init__(self, *args, **kwargs):
        self.key_func = default_key_func

    def make_key(self, key, version=None):
        """Constructs the key used by all other methods. By default it
        uses the key_func to generate a key (which, by default,
        prepends the `key_prefix' and 'version'). An different key
        function can be provided at the time of cache construction;
        alternatively, you can subclass the cache backend to provide
        custom key making behavior.
        """
        if version is None:
            version = self.version

        new_key = self.key_func(key, self.key_prefix, version)
        return new_key

    def add(self, key, value, timeout=None, version=None, callback=None):
        """
        Set a value in the cache if the key does not already exist. If
        timeout is given, that timeout will be used for the key; otherwise
        the default cache timeout will be used.

        Returns True if the value was stored, False otherwise.
        """
        raise NotImplementedError

    def get(self, key, default=None, version=None, callback=None):
        """
        Fetch a given key from the cache. If the key does not exist, return
        default, which itself defaults to None.
        """
        raise NotImplementedError

    def set(self, key, value, timeout=None, version=None, callback=None):
        """
        Set a value in the cache. If timeout is given, that timeout will be
        used for the key; otherwise the default cache timeout will be used.
        """
        raise NotImplementedError

    def delete(self, key, version=None, callback=None):
        """
        Delete a key from the cache, failing silently.
        """
        raise NotImplementedError

    @gen.engine
    def has_key(self, key, version=None, callback=None):
        """
        Returns True if the key is in the cache and has not expired.
        """
        result = gen.Task(self.get, key, version=version)
        callback(result is not None)
