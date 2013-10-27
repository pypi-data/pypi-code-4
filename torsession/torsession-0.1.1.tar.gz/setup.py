# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import torsession

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Development Status :: 5 - Production/Stable
Natural Language :: English
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.0
Programming Language :: Python :: 3.3
Operating System :: MacOS :: MacOS X
Operating System :: Unix
Programming Language :: Python
Programming Language :: Python :: Implementation :: CPython
"""

version = torsession.__version__
description = 'An asynchronous session backend with mongodb for tornado'
long_description = open("README.rst").read()
packages = ['torsession']

setup(
    name='torsession',
    version=version,
    packages=packages,
    description=description,
    long_description=long_description,
    author='Lime YH.Shi',
    author_email='shiyanhui66@gmail.com',
    url='https://github.com/shiyanhui/torsession',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    classifiers=filter(None, classifiers.split('\n')),
    keywords=[
        'torsession', 'mongo', 'mongodb', 'motor', 'session', 'backend',
        'tornado', 'asynchronous'
    ],
    zip_safe=False,
)

