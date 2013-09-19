#coding:utf-8
import logging
import hashlib
import struct

from workertier.backends import BackendUnavailable
from workertier.backends.cache import Cache
from workertier.backends.cache.memcached import MemcachedCache


logger = logging.getLogger(__name__)


class BaseMemcachedClusterCache(Cache):
    hash_algorithm = hashlib.sha256
    hash_bin_format = "QQQQ"

    def __init__(self, port, timeout):
        self.port = port
        self.timeout = timeout

        self._clients = {}
        self._hash_struct = None

    def _get_key_index(self, key):
        if self._hash_struct is None:
            self._hash_struct = struct.Struct(self.hash_bin_format)
        digest = self.hash_algorithm(key).digest()
        return sum(self._hash_struct.unpack(digest))

    def _elect_server(self, key):
        # Naive, low-performance implementation
        ips = self._get_backend_ip_list()
        return ips[self._get_key_index(key) % len(ips)]

    def _create_backend_connection(self, server):
        return MemcachedCache(server, self.port, self.timeout)

    def _get_backend_ip_list(self):
        raise NotImplementedError()

    def _get_backend_connection(self, key):
        server = self._elect_server(key)
        if server not in self._clients:
            logger.debug("Creating new client for %s", server)
            self._clients[server] = self._create_backend_connection(server)
        logger.debug("Using host: %s", server)
        return self._clients[server]

    def get(self, key):
        return self._get_backend_connection(key).get(key)

    def set(self, key, value):
        return self._get_backend_connection(key).set(key, value)


class BaseRemoteMemcachedClusterCache(BaseMemcachedClusterCache):
    def _get_backend_ip_list(self):
        remote = self._get_remote()

        if not remote.ips:
            remote._refresh_server_list()
        if not remote.ips:
            raise BackendUnavailable("No remote server is available")
        return remote.ips

    def _get_remote(self):
        raise NotImplementedError()