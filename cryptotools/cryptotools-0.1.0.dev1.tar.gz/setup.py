#!/usr/bin/env python3
from distutils.core import setup
from cryptotools import __version__, __author__

setup(
    name='cryptotools',
    version='.'.join(str(v) for v in __version__),
    author=__author__,
    author_email='esqaw@ytosi.com',
    license='LICENSE',
    packages=['cryptotools'],
    classifiers=[
        'Programming Language :: Python :: 3.3',
    ],
    url='https://github.com/esqaw/cryptotools',
)
