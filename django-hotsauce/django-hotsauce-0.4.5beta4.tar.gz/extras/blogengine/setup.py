#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009-2010 Etienne Robillard <erob@gthcfoundation.org>
# All rights reserved. 
#
# <LICENSE>
import sys
import os

# N.B: This will fetch latest setuptools with ez_setup.py if setuptools is
# not available.
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

AUTHOR = 'Etienne Robillard'
AUTHOR_EMAIL = 'erob@gthcfoundation.org'
VERSION = '0.4.5'
SUMMARY = 'Python powered blog engine API'
DESCRIPTION = 'unknown'

HOMEPAGE_URL = u'http://gthc.org/projects/blogengine/%s/' % VERSION
KEYWORDS = 'BlogEngine notmm' 
MAINTAINER = u'notmm-discuss@googlegroups.com'
MAINTAINER_EMAIL = MAINTAINER
LICENSE = u'ISC'
PACKAGE_NAME = 'blogengine'
LIBDIR = '.'
#print "Libraries directory: %s" % os.path.realpath(LIBDIR)
#DATA = [('share/doc/notmm', glob('docs/reference/*.rst'))]

# Do import buildutils commands if available!
try:
    import buildutils
except ImportError:
    print "Warning: %r package not found." % 'buildutils'

def resource_string(app_label, filename):
    # A mostly boring resource_string safe to use
    sitedir = os.path.join(os.getcwd(), LIBDIR, app_label)
    fh = file(os.path.join(sitedir, filename), 'r')
    outs = fh.read(); fh.close()
    return outs

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=SUMMARY, 
    long_description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    keywords=KEYWORDS, 
    url=HOMEPAGE_URL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,

    # Include stuff which belong in SVN or mentioned in MANIFEST.in
    include_package_data=True,

    # Location where packages lives
    package_dir={'': LIBDIR},
    packages=find_packages(where=LIBDIR),
    
    #classifiers=[('%s' % item) for item in resource_string('notmm',
    #    'static/classifiers.txt').split('\n') if item is not ""],

    # Extend setuptools with our own command set.
    #entry_points=_commands,
    
    # Packages required when doing `setup.py install`.
    install_requires=[
        'webhelpers>=dev',
        #'decorator>=3.3.2'
    ],
    # Optional but recommended packages
    extras_require={
        'pyyaml'     : ['pyyaml'],
        'pycryptopp' : ['pycryptopp>=0.5.12'],
        'elixir'     : ['Elixir>=0.6.1']
    },
    zip_safe=(sys.version >= 2.5)
)

