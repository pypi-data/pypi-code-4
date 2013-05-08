from zope.interface.declarations import implements
from wm.sampledata.interfaces import ISampleDataPlugin
from zope.component import getUtility
import logging

logger = logging.getLogger('wm.sampledata')


class PluginGroup(object):
    """useful baseclass for grouping plugins by their name
    """

    implements(ISampleDataPlugin)

    PLUGINS = []

    def generate(self, context):
        for plugin in self.PLUGINS:
            plugin = getUtility(ISampleDataPlugin, name=plugin)
            plugin.generate(context)
