#!/usr/bin/env python

"""Installer for yolk."""

from setuptools import setup

from yolk.__init__ import __version__ as VERSION


with open('README.rst') as readme:
    setup(
        name='yolk3k',
        license='BSD License',
        version=VERSION,
        description='Command-line tool for querying PyPI and Python packages '
                    'installed on your system.',
        long_description=readme.read(),
        maintainer='Rob Cakebread',
        author='Rob Cakebread',
        author_email='cakebread @ gmail',
        url='https://github.com/myint/yolk',
        keywords='PyPI,setuptools,cheeseshop,distutils,eggs,package,'
                 'management',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        packages=['yolk', 'yolk.plugins'],
        package_dir={'yolk': 'yolk'},
        entry_points={'console_scripts': ['yolk = yolk.cli:main']},
        test_suite='tests.test_yolk_cli'
    )
