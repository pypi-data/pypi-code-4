__author__ = 'dtilleyshort'
__version__ = '0.1.7'

import os
from setuptools import setup

setup(name='pika_simple_daemon',
    version=__version__,
    url='https://github.com/Tilley/pika_simple_daemon',
    author=__author__,
    author_email="david.tilleyshort@gmail.com",
    description="Simple Pika Daemon",
    long_description = "",
    license='BSD',
    platforms=['linux'],
    packages=['pika_simple_daemon', 'pika_simple_daemon'],
    install_requires=[
        "pika==0.9.12",
        "mock==0.8.0"
    ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
    ],
    zip_safe = False,
)
