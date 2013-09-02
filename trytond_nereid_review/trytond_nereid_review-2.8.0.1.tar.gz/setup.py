#!/usr/bin/env python
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import os
import re
import ConfigParser
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()

major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = []
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append('trytond_%s >= %s.%s, < %s.%s' %
                (dep, major_version, minor_version, major_version,
                    minor_version + 1))
requires.append('trytond >= %s.%s, < %s.%s' %
        (major_version, minor_version, major_version, minor_version + 1))

setup(
    name='trytond_nereid_review',
    version=info.get('version', '0.0.1'),
    description='A pluggable review app',
    author='Openlabs Technologies and Consulting (P) Ltd.',
    url='http://openlabs.co.in/',
    download_url="https://github.com/openlabs/nereid-review",
    package_dir={'trytond.modules.nereid_review': '.'},
    packages=[
        'trytond.modules.nereid_review',
        'trytond.modules.nereid_review.tests',
    ],
    package_data={
        'trytond.modules.nereid_review': info.get('xml', []) + ['tryton.cfg']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Tryton',
        'Topic :: Office/Business',
    ],
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    nereid_review = trytond.modules.nereid_review
    """,
    test_suite='tests',
    test_loader='trytond.test_loader:Loader',
)
