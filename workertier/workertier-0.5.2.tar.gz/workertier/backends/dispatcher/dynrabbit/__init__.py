#coding:utf-8
import functools
import logging
import gevent

from workertier.backends import BackendUnavailable
from workertier.backends.dispatcher.dynrabbit.backoff import ExponentialBackoffStrategy
from workertier.backends.dispatcher.rabbitmq import RabbitMQDispatcher


logger = logging.getLogger(__name__)


def retry_on_error(method):
    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        while 1:
            try:
                ret = method(self, *args, **kwargs)
            except BackendUnavailable as e:
                logger.warning("Backend is unavailable: %s", e)
                self.backoff_strategy.failed()
            else:
                self.backoff_strategy.succeeded()
                return ret
            self.backoff_strategy.wait()
    return wrapped


class DynamicRabbitMQDispatcher(RabbitMQDispatcher):
    """
    A more robust RabbitMQ dispatcher.
    """
    #TODO: Make dispatch more resilient

    def __init__(self, port, virtualhost, user, password, queue):
        super(DynamicRabbitMQDispatcher, self).__init__(None, port, virtualhost, user, password, queue)
        self.backoff_strategy = ExponentialBackoffStrategy()

    @property
    def host(self):
        return self._get_backend_ip()

    def _get_backend_ip(self):
        remote = self._get_remote()

        if not remote.ips:
            remote._refresh_server_list()
        if not remote.ips:
            raise BackendUnavailable("No remote server is available")
        if len(remote.ips) > 1:
            logger.warning("Found multiple backends: %s", ", ".join(remote.ips))
        return sorted(remote.ips)[0]  # Ensure we always use the same IP

    def _get_remote(self):
        raise NotImplementedError()

    def dispatch(self, key):
        gevent.spawn(retry_on_error(RabbitMQDispatcher.dispatch), self, key)

    @retry_on_error
    def _consume(self):
        # TODO: Useless, there is no way we're getting out of there if we don't fail
        # TODO: Kind of sucks that we have no way of telling if we're good here
        # TODO: What happens here is that every time we have to reconnect, we'll backoff a bit more!
        # TODO: Make the separation of tasks between the two rabbit dispatchers clearer
        super(DynamicRabbitMQDispatcher, self)._consume()
