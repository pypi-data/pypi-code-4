#!/usr/bin/env python
"""
sentry-penelope
=============

An extension for Sentry which integrates with penelope. Specifically, it allows you to easily create
issues from events within Sentry.

:copyright: (c) 2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from setuptools import setup, find_packages


tests_require = [
    'nose',
]

install_requires = [
    'sentry>=5.0.0',
    'requests'
]

setup(
    name='sentry-penelope',
    version='0.1',
    author='Andrew Mleczko',
    author_email='penelopedev@redturtle.it',
    url='http://github.com/getpenelope/sentry-penelope',
    description='A Sentry extension which integrates with penelope.',
    long_description=__doc__,
    license='BSD',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite='runtests.runtests',
    include_package_data=True,
    entry_points={
       'sentry.apps': [
            'penelope = sentry_penelope',
        ],
       'sentry.plugins': [
            'penelope = sentry_penelope.plugin:PenelopePlugin'
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
