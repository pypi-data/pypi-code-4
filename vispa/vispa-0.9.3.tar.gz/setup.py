#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import os

ignore_extensions = ['.py', '.pyc', '.pyo', '.orig']
files = []
packages = []

for wroot, wdirs, wfiles in os.walk('vispa'):
    for name in wfiles:
        if name == "__init__.py":
            packages.append(wroot.replace(os.sep, ".").strip(". \t\n\r"))
        base, ext = os.path.splitext(name)
        if not ext in ignore_extensions:
            files.append(os.path.join(wroot[6:], name))

setup (
    name='vispa',
    version='0.9.3',
    description='VISPA - Integrated Development Environment for Physicists',
    author='VISPA Project',
    author_email='vispa@lists.rwth-aachen.de',
    url='http://vispa.physik.rwth-aachen.de/',
    license='GNU GPL v2',
    packages=packages,
    package_data={'vispa': files},
    scripts=['bin/vispa', 'bin/vispad'],
    install_requires=['sqlalchemy', 'mako', 'cherrypy', 'pushy', 'rpyc'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: CherryPy',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: JavaScript',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development',
    ]
)