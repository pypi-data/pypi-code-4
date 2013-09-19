#coding:utf-8
import logging

import gevent.dns
import gevent.socket

from workertier.backends.remote.base import BaseRemoteBackend


logger = logging.getLogger(__name__)


class DNSRemoteBackend(BaseRemoteBackend):
    def __init__(self, hostname, refresh_signal=None):
        super(DNSRemoteBackend, self).__init__(refresh_signal)
        self.hostname = hostname

    def _get_servers_list(self):
        ttl, ips = gevent.dns.resolve_ipv4(self.hostname)
        return [gevent.socket.inet_ntoa(ip) for ip in sorted(ips)]
