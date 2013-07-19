from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Elements Storage',
    icon='hdd',
    dependencies=[
        PluginDependency('main'),
        PluginDependency('services'),
    ],
)


def init():
    import projects.main
    import video.main
