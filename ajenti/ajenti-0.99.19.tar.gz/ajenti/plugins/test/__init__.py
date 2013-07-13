from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Test',
    icon=None,
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import main
