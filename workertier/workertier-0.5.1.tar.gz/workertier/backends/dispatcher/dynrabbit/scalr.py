#coding:utf-8
from workertier.backends.remote.scalr import ScalrRemoteBackend
from workertier.backends.dispatcher.dynrabbit import DynamicRabbitMQDispatcher


class ScalrDynRabbitDispatcher(DynamicRabbitMQDispatcher):
    def __init__(self, ip_list_home, rabbitmq_role, port, virtualhost, user, password, queue, refresh_signal=None):
        super(ScalrDynRabbitDispatcher, self).__init__(port, virtualhost, user, password, queue)
        self.remote = ScalrRemoteBackend(ip_list_home, rabbitmq_role, refresh_signal)

    def _get_remote(self):
        return self.remote
