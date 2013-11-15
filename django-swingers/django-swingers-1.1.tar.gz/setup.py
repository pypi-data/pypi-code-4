#!/usr/bin/env python
"""
Swingers
========

TODO: (v0.9)
Swingers provides authentication and auditing of models for DEC applications.

:copyright: (c) 2013 Department of Parks & Wildlife, see AUTHORS
            for more details.
:license: Apache License, Version 2.0, see LICENSE for more details.
"""
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from pkg_resources import parse_version

import os

# Hack to prevent stupid "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when running `python
# setup.py test` (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
for m in ('multiprocessing', 'billiard'):
    try:
        __import__(m)
    except ImportError:
        pass


class test(TestCommand):
    user_options = TestCommand.user_options + [
        ('with-xunit', None, "Enable xunit"),
        ('xunit-file=', None, "Xunit file"),
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.with_xunit = False
        self.xunit_file = ''


tests_require = [
    'nose',
    'django-nose',
    'mock>=1.0.1',
    'flake8>=1.5',
    'selenium>=2.25.0',
    'unittest2',
    'coverage>=3.5.3',
    'pep8',
    'pyflakes',
    'psycopg2',
]


django = 'django>=1.4.2'
if os.environ.get('DJANGO'):
    if parse_version(os.environ.get('DJANGO')) >= parse_version('1.4.2'):
        django = 'django=={0}'.format(os.environ.get('DJANGO'))
    else:
        raise Exception('django-swingers requires django>=1.4.2')


install_requires = [
    django,
    'django-model-utils',
    'requests>=0.14.2',
    'south>=0.7.6',
    'django-reversion>=1.7',
    'django-auth-ldap>=1.1.2',
    'django-immutablemodel>=0.3.3',
    'django-guardian>=1.0.4',
    'django-browserid>=0.8',
    'django-redis>=3.1.7',
    'django-redis-sessions>=0.3.1',
    'django-extensions>=1.0.0',
    'django-debug-toolbar>=0.9.4',
    'django-compressor',
    'unidecode>=0.04.12',
    'django-crispy-forms',
    'python-magic',
    'django-htmlmin',   # HTML minification
    'fabric',           # management commands
    'lxml',             # JsCssCompressor
    'BeautifulSoup',    # JsCssCompressor
]

version = __import__('swingers').get_version()

setup(
    name='django-swingers',
    version=version,
    author='Adon Metcalfe, Ashley Felton, Nick Sandford, Tomas Krajcaz',
    author_email=('adon.metcalfe@dpaw.wa.gov.au, ashley.felton@dpaw.wa.gov.au,'
                  ' nick.sandford@dpaw.wa.gov.au, tomas.krajca@dpaw.wa.gov.au'
                  ),
    url='https://bitbucket.org/dpaw/django-swingers',
    description=('Library of common utilities, templates and django'
                 ' customizations used throughout '
                 '`Department of Parks and Wildlife '
                 '<http://dpaw.wa.gov.au/>`_.'),
    packages=find_packages(exclude=['docs']),
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='swingers.tests.runtests.runtests',
    scripts=['swingers/bin/swingers-admin.py'],
    cmdclass={'test': test},
    license='Apache License, Version 2.0',
    include_package_data=True,
    keywords="django utilities authentication tools helpers dpaw",
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
