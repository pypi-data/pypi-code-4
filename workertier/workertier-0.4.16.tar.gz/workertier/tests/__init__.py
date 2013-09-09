#coding:utf-8
import collections
from workertier.backends.remote.base import BaseRemoteBackend


class TestRemote(BaseRemoteBackend):
    def __init__(self, ip_lists):
        super(TestRemote, self).__init__()
        self.ip_lists = collections.deque(ip_lists)
        self.ip_lists.rotate(1)  # We're going to rotate again.

    def _get_servers_list(self):
        self.ip_lists.rotate(-1)
        return self.ip_lists[0]