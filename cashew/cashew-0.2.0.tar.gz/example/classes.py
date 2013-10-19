### "imports"
from cashew import Plugin, PluginMeta

### "create-plugin-base-class"
class Data(Plugin):
    """
    Base class for plugins which present data in various ways.
    """
    __metaclass__ = PluginMeta

    ### "methods"
    def __init__(self, data):
        self.data = data

    def present(self):
        raise Exception("not implemented")
