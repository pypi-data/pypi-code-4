import os
from distutils.core import setup

setup(
    name='bus_component',
    packages = ["bus_component"],
    package_dir = { 'bus_component' : 'lib' },
    description='amqp bus communication lirbrary to pass infromation',
    version='0.1.0',
    author="Borrey Kim",
    author_email="borrey@gmail.com",
    url="git://github.com/borrey/bus-component.git",
    keywords=['bus','amqp'],
    requires=['message_amqp', 'event_amd'],
    long_description = """\
    Python module to handle messaging with other message_amqp services.
    """
)
