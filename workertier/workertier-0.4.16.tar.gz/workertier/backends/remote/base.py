#coding:utf-8
import logging

from workertier.utils.signal_handler import SignalHandler, find_signum


logger = logging.getLogger(__name__)


class BaseRemoteBackend(object):
    """
    A backend that is available on a remote host.
    """

    def __init__(self, refresh_signal=None):
        """
        :param refresh_signal: An optional signal (or signal name) we should listen on to refresh our IP list
        """
        self.ips = []
        self.signal_handler = None

        if refresh_signal is not None:
            self.signal_handler = SignalHandler(find_signum(refresh_signal), self._refresh_server_list)

    def _refresh_server_list(self):
        self.ips = self._get_servers_list()
        logger.debug("Refreshed server list: now %s hosts", len(self.ips))
        map(logger.debug, ["Host at: %s"]*len(self.ips), self.ips)

    def _get_servers_list(self):
        raise NotImplementedError()

