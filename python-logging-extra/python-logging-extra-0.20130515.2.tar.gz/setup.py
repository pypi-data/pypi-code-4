#! /usr/bin/env python

import os
from distutils.core import setup

setup(
    name         = 'python-logging-extra',
    version      = '0.20130515.2',
    packages     = ['loggingx'],
    data_files   = [('share/doc/python-loggingx', ['README.rst'])],
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),

    # Metadata
    author       = 'David Villa Alises',
    author_email = 'David.Villa@gmail.com',
    description  = 'Generic utilities for the Python logging facility',
    license      = 'GPLv3',
    url          = ' https://bitbucket.org/DavidVilla/python-logging-extra'
)
