#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

import jpath

setup(
    name='jpath',
    py_modules=['jpath'],
    version=jpath.__version__,
    description='Access nested dicts and lists using JSON-like path notation.',
    long_description=jpath.__doc__,
    author='Radomir Dopieralski',
    author_email='jpath@sheep.art.pl',
    url = 'http://www.stxnext.pl/open-source/jpath',
    download_url = 'https://bitbucket.org/thesheep/jpath/get/tip.tar.gz',
    classifiers = [
        'Development Status :: 6 - Mature',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
        'License :: OSI Approved :: MIT License',
    ],
)
