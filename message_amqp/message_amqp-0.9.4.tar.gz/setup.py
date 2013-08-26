import os
from distutils.core import setup

setup(
    name='message_amqp',
    packages = ["message_amqp"],
    package_dir = { 'message_amqp' : 'lib' },
    description='amqp setup for python nodejs and php',
    version='0.9.4',
    author="Borrey Kim",
    author_email="borrey@gmail.com",
    url="git@github.com:borrey/message-amqp.git",
    download_url="https://bitbucket.org/borreykim/message-amqp/downloads/message_amqp-0.9.4.tar.gz",
    keywords=['amqp'],
    requires=['event_amd'],
    long_description = """\
    Python module to handle messaging with other message_amqp services.
    """
)
