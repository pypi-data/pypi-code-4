#!/usr/bin/env python

import distutils.core
import distutils.util

try:
    from distutils.command.build_py import build_py_2to3 \
        as build_py
except ImportError:
    from distutils.command.build_py import build_py


platform = distutils.util.get_platform()

if not platform.startswith('linux'):
    raise Exception('inotify is linux-specific, and does not work on %s' %
                    platform)

distutils.core.setup(
    name='python-inotify',
    version='0.6-test',
    description='Interface to Linux inotify subsystem',
    author="Jan Kanis",
    author_email='jan.code@jankanis.nl',
    license='LGPL',
    platforms='Linux',
    packages=['inotify'],
    url='https://bitbucket.org/JanKanis/python-inotify',
    ext_modules=[distutils.core.Extension('inotify._inotify',
                                          ['inotify/_inotify.c'])],
    cmdclass={'build_py': build_py},
    )
