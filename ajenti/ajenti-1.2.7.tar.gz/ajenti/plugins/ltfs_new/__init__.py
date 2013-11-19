from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='LTFS Archive',
    icon='list',
    dependencies=[
        PluginDependency('main'),
    ],
)


def init():
    import archive.main
    import jobs.main
    import library.main
    import tapegroups.main
