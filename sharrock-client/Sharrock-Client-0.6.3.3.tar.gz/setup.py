#!/usr/bin/env python
try:
    from setuptools import setup 
except ImportError, err:
    from distutils.core import setup

from sharrock import VERSION

setup(
    name='Sharrock-Client',
    version='.'.join(map(str,VERSION)),
    description='Client for Sharrock Python RPC framework.',
    packages=['sharrock'],
    include_package_data=True,
    license='BSD',
    author='Loren Davie',
    author_email='code@axilent.com',
    url='https://github.com/Axilent/sharrock-client',
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)