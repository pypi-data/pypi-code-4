#coding:utf-8
import os
import logging

from workertier.backends.remote.base import BaseRemoteBackend


logger = logging.getLogger(__name__)


class ScalrRemoteBackend(BaseRemoteBackend):
    def __init__(self, ip_list_home, role_name, refresh_signal=None):
        super(ScalrRemoteBackend, self).__init__(refresh_signal)
        self.ip_list_home = ip_list_home
        self.role_name = role_name

    def _get_servers_list(self):
        ip_path = os.path.join(self.ip_list_home, self.role_name)
        return os.listdir(ip_path)
