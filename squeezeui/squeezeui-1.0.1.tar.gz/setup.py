#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  Squeezeui - Graphical user interface for Squeezebox players.

import os
from setuptools import setup
# from distutils.core import setup

def _scripts():
    if os.name == 'nt':
        return ['squeezeui-controller.py', 'squeezeui-player.py']
    else:
        return ['bin/squeezeui']

setup(name='squeezeui',
    version='1.0.1',
    description='Graphical user interface for Squeezebox players.',
    long_description=open('README').read(),
    author='Frode Holmer',
    author_email='fholmer@gmail.com',
    license='GPLv3',
    url='https://bitbucket.org/fholmer/squeezeui',
    keywords='Squeezebox Squeezelite',
    packages=['squeezeui', 'squeezeui.controllers', 'squeezeui.models'],
    package_data={'squeezeui': ['views/*.*', 'views/*/*.*']},
    scripts=_scripts(),
    requires=['PySide (>=1.1.2)', 'jsonrpclib (>=0.1.6)'], # jsonrpclib-pelix
    provides=['squeezeui (1.0.1)'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Players'])
