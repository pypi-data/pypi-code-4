#!/usr/bin/env python

from distutils.core import setup

long_desc = '''

Persei
------

Ease the crossing - or straddling - of the Python 2 vs Python 3 border, with Persei, a group of helpful classes for dealing with string and binary data in a consistent manner across Python 2.6-3.3.

The name is short for "Unicode-Persei 8", where the 8 stands for UTF-8. If you don't get the reference, that's bad news, but don't fry your brain on it.

The code is all migrated from EJTP.util.py2and3, which was too globally useful to keep locked up as an EJTP dependency. It was written by Moritz Sichert, with various modifications here and there by others. EJTP 0.9.6+ will depend on Persei as an external dependency.
'''

setup(
	name = 'persei',
	version = '0.1.0',
	description = 'Normalization layer for bytestream and string data across Python 2 and 3',
    long_description = long_desc,
	author = 'Moritz Sichert',
	url = 'https://github.com/campadrenalin/persei/',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Environment :: Console',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'Topic :: Internet',
    ],
    py_modules = ['persei']
)
