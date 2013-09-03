#coding:utf-8
import random
import logging
import zlib
import signal

import gevent

from workertier.backends import BackendUnavailable
from workertier.backends.cache import Cache
from workertier.backends.cache.memcached import MemcachedCache


logger = logging.getLogger(__name__)


def find_signum(name_or_signum):
    try:
        signum = int(name_or_signum)
    except ValueError:
        signum = getattr(signal, name_or_signum)
    return signum


class BaseMemcachedClusterCache(Cache):
    def __init__(self, port, timeout, refresh_signal=None):
        """
        :param refresh_signal: A signal number (e.g. 10) or name (e.g. SIGUSR1) to attach _refresh_servers_list to.
        """
        self.port = port
        self.timeout = timeout

        self._ips = []
        self._clients = {}

        if refresh_signal is not None:
            signum = find_signum(refresh_signal)
            if signum is None:
                raise TypeError("refresh_signal was not None, but was not a valid signal name or signum")
            gevent.signal(signum, self._refresh_server_list)

    def _get_servers_list(self):
        raise NotImplementedError()

    def _refresh_server_list(self):
        self._ips = self._get_servers_list()
        logger.debug("Refreshed Memcached server list: now %s hosts", len(self._ips))
        map(logger.debug, ["Host at: %s"]*len(self._ips), self._ips)

    def _get_server(self, key):
        # Naive, low-performance implementation
        assert self._ips, "_find_server should not have been called with self._ips == []"
        return self._ips[zlib.crc32(key) % len(self._ips)]

    def _get_cache(self, key):
        server = self._get_server(key)
        if  server not in self._clients:
            logger.debug("Creating new client for %s", server)
            self._clients[server] = MemcachedCache(server, self.port, self.timeout)
        logger.debug("Using host: %s", server)
        return self._clients[server]

    def get_cache(self, key):
        # Refresh our servers list 10% of the time (we should use signals)
        if random.random() < 0.1 or not self._ips:
            self._refresh_server_list()

        if not self._ips:
            raise BackendUnavailable("No servers found")

        return self._get_cache(key)

    def get(self, key):
        return self.get_cache(key).get(key)

    def set(self, key, value):
        return self.get_cache(key).set(key, value)
