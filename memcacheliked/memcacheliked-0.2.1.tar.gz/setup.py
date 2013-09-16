#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='memcacheliked',
        version='0.2.1',
        description='Simple framework for writing daemons using the memcache interface for storing data',
        author='Vicious Red Beam',
        author_email='vicious.red.beam@gmail.com',
        packages=['memcacheliked'],
        install_requires=['diesel'],
        license='MIT',
        url='https://bitbucket.org/ViciousRedBeam/memcacheliked',
        )

