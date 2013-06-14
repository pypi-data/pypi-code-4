#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from distutils.core import setup, Extension


DISTUTILS_DEBUG = True


lirc_ext = Extension(
    'lirc',
    include_dirs=['/usr/include/lirc/'],
    libraries=['lirc_client'],
    library_dirs=['/usr/lib'],
    sources=['lirc.c']
)

setup(
    name='python-lirc',
    version='1.0',
    description='Python bindings for LIRC.',
    author='Thomas Preston',
    author_email='thomasmarkpreston@gmail.com',
    license='GPLv3+',
    url='https://github.com/tompreston/python-lirc',
    ext_modules=[lirc_ext],
    long_description="Python LIRC extension written in Cython for Python 3 "
        "(and 2).",
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3 or "
        "later (AGPLv3+)",
        "Programming Language :: Cython",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='lirc cython remote ir infrared',
)
