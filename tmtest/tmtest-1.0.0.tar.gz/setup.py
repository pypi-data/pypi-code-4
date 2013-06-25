#!/usr/bin/env python

import sys
import os
from distutils.core import setup

_top_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_top_dir, "lib"))
try:
    import tmtest
finally:
    del sys.path[0]

setup(name='tmtest',
    version=tmtest.__version__,
    description="a fledgling personal test lib",
    classifiers=[c.strip() for c in """
        License :: OSI Approved :: MIT License
        Operating System :: OS Independent
        Programming Language :: Python :: 2
        Programming Language :: Python :: 2.4
        Programming Language :: Python :: 2.5
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.1
        Topic :: Software Development :: Libraries :: Python Modules
        """.split('\n') if c.strip()],
    keywords='tmtest',
    author='Trent Mick',
    author_email='trentm@gmail.com',
    maintainer='Trent Mick',
    maintainer_email='trentm@gmail.com',
    url='http://github.com/trentm/tmtest',
    license='MIT',
    scripts=['bin/tmtester'],
    packages=['tmtest'],
    package_dir={"": "lib"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "PyCrypto >= 2.5"
    ]
)

