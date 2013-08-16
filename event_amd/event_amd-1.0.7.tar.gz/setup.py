import os
from distutils.core import setup

setup(
    name='event_amd',
    packages = ["event_amd"],
    description='Port for EventEmitter from nodejs',
    version='1.0.7',
    author="Borrey Kim",
    author_email="borrey@gmail.com",
    url="https://bitbucket.org/borreykim/event_amd",
    download_url="https://bitbucket.org/borreykim/event_amd/downloads/event_amd-1.0.6.tar.gz",
    keywords=['events'],
    long_description = """\
    This is an inital step to port over EventEmitter of nodejs. This is done with the goal of having libraries that are cross platform so that cross comunication is easier, and collected together.
    """
)
