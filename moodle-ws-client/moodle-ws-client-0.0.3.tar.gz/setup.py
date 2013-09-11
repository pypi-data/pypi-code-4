#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from setuptools import setup

import os
import moodle_ws_client

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = 'moodle-ws-client',
    version=moodle_ws_client.__version__,
    url='https://github.com/kotejante/python-moodle',
    license='GNU Affero General Public License v3',
    author='Francisco Moreno',
    author_email='packo@assamita.net',
    description='Moodle web services (2.5) connection library ',
    long_description=(read('README')),
    packages=['moodle_ws_client'],
    zip_safe=False,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
)

