# -*- coding: utf-8 -*-
"""Installer for mls.fabfile."""

from setuptools import setup, find_packages

version = '0.2'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')

setup(
    name='mls.fabfile',
    version=version,
    description='Deploy and manage Propertyshelf MLS applications using Fabric.',
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python',
    ],
    keywords='fabric python mls deployment',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='https://github.com/propertyshelf/mls.fabfile',
    download_url='http://pypi.python.org/pypi/mls.fabfile',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir = {'': 'src'},
    namespace_packages=['mls'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'Fabric',
        'PyChef',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
