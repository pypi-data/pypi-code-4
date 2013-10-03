#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='airbrite',
    version='0.1',
    description='Airbrite python bindings',
    author='Elvio Toccalino',
    author_email='etoccalino@creativa77.com.ar',
    url='https://www.airbrite.io/',
    install_requires=['requests >= 2.0.0', 'nose >= 1.3.0'],
    packages=['airbrite', 'airbrite.tests'],
    test_suite='airbrite.tests'
)
