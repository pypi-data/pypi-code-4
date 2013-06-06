from pwmanager.nodes.models import Node
from pwserver.config import ConfigSource


class PwManagerConfigSource(ConfigSource):

    def __init__(self):
        super(PwManagerConfigSource, self).__init__()

    def get_node_config(self, node_name):
        group, name = self._split_name(node_name)

        node = Node.objects.get(short_name=name, group__short_name=group)
        if node.group.short_name != group:
            return None

        return node.get_context()

    def get_node_list(self):
        return [node.format_full_name() for node in Node.objects.all()]

    def _split_name(self, node_name):
        return node_name.split('::')[0:2]


