#!/usr/bin/env python

PROJECT = 'inkwave'
VERSION = '0.3'

from setuptools import (
    setup,
    find_packages,
)


try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    long_description = ''


setup(
    name=PROJECT,
    version=VERSION,

    description='Framework for building static websites',
    long_description=long_description,

    author='Boris Kaul',
    author_email='me@boriskaul.com',

    url='http://www.inkwave.org',
    download_url='https://github.com/localvoid/inkwave/tarball/master',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Intended Audience :: Developers',
        'Environment :: Console',
    ],

    platforms=['Any'],

    scripts=[],

    provides=[],
    install_requires=[
        'cliff',
        'sqlalchemy',
        'webob',
        'lxml',
        'cssselect',
        'PyYAML',
        'filespy',
    ],

    packages=find_packages(),
    include_package_data=True,


    entry_points={
        'console_scripts': [
            'inkwave = inkwave.cli:main'
        ],
        'inkwave.cli': [
            'data = inkwave.commands.data:Data',
            'build = inkwave.commands.build:Build',
            'serve = inkwave.commands.serve:Serve',
        ],
    },

    zip_safe=False,
)
