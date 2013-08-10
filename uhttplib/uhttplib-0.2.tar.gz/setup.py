#!/usr/bin/env python

import os
import sys
from distutils.core import setup

def long_description():
    """Get the long description from the README"""
    return open(os.path.join(sys.path[0], 'README.rst')).read()

setup(
    author='Erik van Zijst',
    author_email='erik.van.zijst@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
    ],
    description='Unix domain socket support for httplib.',
    download_url='https://bitbucket.org/evzijst/uhttplib/downloads/uhttplib-0.2.tar.gz',
    keywords='httplib unixdomain',
    long_description=long_description(),
    license='MIT',
    name='uhttplib',
    packages=['uhttplib'],
    requires=['httplib'],
    url='https://bitbucket.org/evzijst/uhttplib',
    version='0.2'
)
