#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#
"""Collection of reusable WSGI applications

Copyright (C) 2007-2012 Etienne Robillard <erob@gthcfoundation.org>
All rights reserved. 
"""

import sys, os, posixpath
from setuptools import setup, find_packages

PACKAGE_NAME = 'notmm-extras'
AUTHOR = u'Etienne Robillard'
AUTHOR_EMAIL = u'erob@gthcfoundation.org'
VERSION = u'0.4.5'
SUMMARY = u'A collection of reusable WSGI applications'
# DESCRIPTION =  __doc__
HOMEPAGE_URL = u'http://notmm.org/'
KEYWORDS = 'notmm'
MAINTAINER = u'erob@gthcfoundation.org'
MAINTAINER_EMAIL = MAINTAINER
LICENSE = u'ISC'

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=SUMMARY, 
    #long_description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    keywords=KEYWORDS, 
    url=HOMEPAGE_URL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,

    # Include stuff which belong in SVN or mentioned in MANIFEST.in
    # include_package_data=True,

    # Location where packages lives
    package_dir={
        '': '.',
        'argparse2': '.'},
    packages=find_packages(),

    #classifiers=[('%s' % item) for item in safe_resource_string('notmm',
    #    'static/classifiers.txt').split('\n') if item is not ""],
    # Extend setuptools with our own command set.
    #entry_points=_commands,
    
    # Packages required when doing `setup.py install`.
    #install_requires=['MoinMoin==1.8.9'],
    zip_safe=False
)

