#coding:utf-8
import logging
import socket

from pymemcache.client import Client, MemcacheError, MemcacheIllegalInputError
from workertier.backends import BackendUnavailable, InvalidKey
from workertier.backends.cache import Cache
#TODO: monkey.patch_all here.


logger = logging.getLogger(__name__)



class MemcachedCache(Cache):
    def __init__(self, host, port):
        logger.debug("Connecting to Memcached")
        self.client = Client((host, port))

    def _invoke_command(self, command, *args, **kwargs):
        try:
            return command(*args, **kwargs)
        except MemcacheIllegalInputError:
            raise InvalidKey()
        except (MemcacheError, socket.error, socket.timeout):
            raise BackendUnavailable()

    def get(self, key):
        return self._invoke_command(self.client.get, key)

    def set(self, key, value):
        return self._invoke_command(self.client.set, key, value)
