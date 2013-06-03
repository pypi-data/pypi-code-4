#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup (
    name='vispa-augeroffline',
    version='0.1.1',
    description='VISPA Auger Offline Extension',
    author='VISPA Project',
    author_email='vispa@lists.rwth-aachen.de',
    url='http://vispa.physik.rwth-aachen.de/',
    license='GNU GPL v2',
    packages=find_packages(),
    include_package_data = True,
    install_requires=['vispa>=0.9.2', 'lxml'],
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