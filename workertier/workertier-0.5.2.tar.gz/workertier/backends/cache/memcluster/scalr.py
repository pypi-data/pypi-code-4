#coding:utf-8
from workertier.backends.remote.scalr import ScalrRemoteBackend
from workertier.backends.cache.memcluster import BaseRemoteMemcachedClusterCache


class ScalrMemcachedClusterCache(BaseRemoteMemcachedClusterCache):
    def __init__(self, ip_list_home, memcached_role, port, timeout, refresh_signal=None):
        """
        :param ip_list_home: The path to Scalr's IP list folder (usually /etc/scalr/private.d/hosts)
        :param memcached_role: The name of the memcached role, or behaviour (memcached)
        """
        super(ScalrMemcachedClusterCache, self).__init__(port, timeout)
        self.remote = ScalrRemoteBackend(ip_list_home, memcached_role, refresh_signal)

    def _get_remote(self):
        return self.remote
