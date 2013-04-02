#!/usr/bin/env python
# -*- coding: latin1 -*- vim: ts=8 sts=4 sw=4 si et tw=79
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from os.path import dirname, abspath, join

def read(name):
    fn = join(dirname(abspath(__file__)), name)
    return open(fn, 'r').read()

__author__ = "Tobias Herp <tobias.herp@gmx.net>"
VERSION = (0,
           1,   # initial version
           4,   # thebops.opo: add_trace_option/DEBUG
           ## the Subversion revision is added by setuptools:
           # 'rev-%s' % '$Rev: 950 $'[6:-2],
           )
__version__ = '.'.join(map(str, VERSION))

setup(name='thebops'
    , version=__version__
    , packages=find_packages()
    , entry_points = {
        'console_scripts': [
            '%s = thebops.tools.%s:main' % (s, s.replace('-', '_'))
            for s in [
                'rexxbi_demo',
                'termwot_demo',
                'shtools_demo',
                'opo_demo',
                # 'py2',
                ]
            ] + [
            '%s = thebops.%s:main' % (s, s)
            for s in ['modinfo',
                      ]
            ],
        }
    , author='Tobias Herp'
    , author_email='tobias.herp@gmx.net'
    , namespace_packages = ['thebops',
                            'thebops.tools',
                            ]
    , description="Tobias Herp's bag of Python stuff"
    , license='GPL'
    , long_description=read('README.txt')
    )

