#coding:utf-8
import logging

from workertier.backends import BackendUnavailable
from workertier.backends.dispatcher import Dispatcher
from workertier.backends.dispatcher.rabbitmq import RabbitMQDispatcher


logger = logging.getLogger(__name__)


class BaseDynRabbitDispatcher(Dispatcher):
    def __init__(self, port, virtualhost, user, password, queue):
        super(BaseDynRabbitDispatcher, self).__init__()

        self.port = port
        self.virtualhost = virtualhost
        self.user = user
        self.password = password
        self.queue = queue

        self._clients = {}

    def _create_backend_connection(self, ip):
        return RabbitMQDispatcher(ip, self.port, self.virtualhost, self.user, self.password, self.queue)

    def _get_backend_ip(self):
        raise NotImplementedError()

    def _get_backend_connection(self):
        backend_ip = self._get_backend_ip()
        if backend_ip not in self._clients:
            self._clients[backend_ip] = self._create_backend_connection(backend_ip)
        return self._clients[backend_ip]

    def dispatch(self, key):
        return self._get_backend_connection().dispatch(key)

    def start_consumer(self, message_consumer):
        return self._get_backend_connection().start_consumer(message_consumer)


class BaseRemoteDynRabbitDispatcher(BaseDynRabbitDispatcher):
    def _get_backend_ip(self):
        remote = self._get_remote()

        if not remote.ips:
            remote._refresh_server_list()
        if not remote.ips:
            raise BackendUnavailable("No remote server is available")
        if len(remote.ips) > 1:
            logger.warning("Found multiple backends: %s", ", ".join(remote.ips))

        return remote.ips[0]

    def _get_remote(self):
        raise NotImplementedError()