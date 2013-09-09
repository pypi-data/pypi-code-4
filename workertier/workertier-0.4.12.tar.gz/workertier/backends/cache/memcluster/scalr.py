#coding:utf-8
import os

from workertier.backends.cache.memcluster import BaseMemcachedClusterCache


class ScalrMemcachedClusterCache(BaseMemcachedClusterCache):
    def __init__(self, ip_list_home, memcached_role, port, timeout, refresh_signal=None):
        """
        :param ip_list_home: The path to Scalr's IP list folder (usually /etc/scalr/private.d/hosts)
        :param memcached_role: The name of the memcached role, or behaviour (memcached)
        """
        super(ScalrMemcachedClusterCache, self).__init__(port, timeout, refresh_signal)

        self.ip_list_home = ip_list_home
        self.memcached_role = memcached_role

    def _get_servers_list(self):
        ip_path = os.path.join(self.ip_list_home, self.memcached_role)
        return os.listdir(ip_path)
