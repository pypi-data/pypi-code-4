from abc import ABCMeta, abstractmethod


class ConfigSource(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_node_list(self):
        """
        Return full list of node names
        """
        return []

    @abstractmethod
    def get_node_config(self, node_name):
        """
        Get host config for one host
        """
        return {}
