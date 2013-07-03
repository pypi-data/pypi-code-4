#!/usr/bin/env python
"""
sentry-uploads
==============

An extension for Sentry which allows large files to be uploaded with errors.

:copyright: (c) 2013 by Process Systems Enterprise
:license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages

install_requires = [
    'sentry>=5.4.0',
    'raven>=3.2.1',
]

setup(
    name='sentry-uploads',
    version='0.1.0',
    author='Duane Griffin',
    author_email='duaneg@dghda.com',
    url='http://github.com/duaneg/sentry-uploads',
    description='A Sentry extension which allows file uploads.',
    long_description=__doc__,
    license='BSD',
    packages=find_packages(),
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'sentry-upload = sentry_uploads.scripts.runner:main',
        ],
        'sentry.apps': [
            'file = sentry_uploads',
        ],
        'sentry.plugins': [
            'file = sentry_uploads.plugin:UploadsPlugin'
        ],
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
