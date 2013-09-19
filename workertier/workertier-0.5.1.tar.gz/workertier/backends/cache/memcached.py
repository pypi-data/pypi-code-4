#coding:utf-8
import logging

import gevent.socket
from pymemcache.client import Client, MemcacheError, MemcacheIllegalInputError

from workertier.backends import BackendUnavailable, InvalidKey
from workertier.backends.cache import Cache
from workertier.backends.pool import ConnectionPool, Connection


logger = logging.getLogger(__name__)


class MemcachedConnection(Connection):
    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.client = None

        super(MemcachedConnection, self).__init__()

    def _get_client(self):
        if self.client is None:
            self.client = Client((self.host, self.port), connect_timeout=self.timeout,
                                 timeout=self.timeout, socket_module=gevent.socket)
        return self.client

    def _invoke_command(self, command, *args, **kwargs):
        try:
            return command(*args, **kwargs)
        except MemcacheIllegalInputError:
            raise InvalidKey()
        except (MemcacheError, gevent.socket.error) as e:
            self.broken = True
            logger.warning("Connection error (%s:%s): %s", self.host, self.port, e)

    def get(self, key):
        return self._invoke_command(self._get_client().get, key)

    def set(self, key, value):
        return self._invoke_command(self._get_client().set, key, value)


class MemcachedCache(Cache, ConnectionPool):
    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout

        super(MemcachedCache, self).__init__()

    def _create_connection(self):
        return MemcachedConnection(self.host, self.port, self.timeout)

    def _invoke_command(self, command_name, *args, **kwargs):
        with self._acquire_connection() as connection:
            with connection.raise_if_broken(BackendUnavailable):
                return getattr(connection, command_name)(*args, **kwargs)

    def get(self, key):
        return self._invoke_command("get", key)

    def set(self, key, value):
        return self._invoke_command("set", key, value)
