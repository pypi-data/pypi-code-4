from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Elements Media Library',
    icon='hdd',
    dependencies=[
        PluginDependency('elements'),
    ],
)


def init():
    import clientui.http
    import clientui.main
