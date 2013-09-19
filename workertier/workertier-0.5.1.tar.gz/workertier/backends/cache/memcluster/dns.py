#coding:utf-8
import logging

from workertier.backends.cache.memcluster import BaseRemoteMemcachedClusterCache
from workertier.backends.remote.dns import DNSRemoteBackend


logger = logging.getLogger(__name__)


class DNSMemcachedClusterCache(BaseRemoteMemcachedClusterCache):
    def __init__(self, domain, port, timeout, refresh_signal=None):
        super(DNSMemcachedClusterCache, self).__init__(port, timeout)
        self.remote = DNSRemoteBackend(domain, refresh_signal)

    def _get_remote(self):
        return self.remote
