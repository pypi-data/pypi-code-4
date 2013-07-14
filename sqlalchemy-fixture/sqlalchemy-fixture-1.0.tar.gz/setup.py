
import sys, os
from setuptools import setup, find_packages
import pydoc


setup(
    name = 'sqlalchemy-fixture',
    version = 1.0,
    author = 'Kumar McMillan & Kirill Ivanov',
    author_email = 'efreeze@mail.ru',
    description = '',
    classifiers = [ 'Environment :: Other Environment',
                    'Intended Audience :: Developers',
                    (   'License :: OSI Approved :: GNU Library or Lesser '
                        'General Public License (LGPL)'),
                    'Natural Language :: English',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Topic :: Software Development :: Testing',
                    'Topic :: Software Development :: Quality Assurance',
                    'Topic :: Utilities'],
    long_description = '',
    license = 'GNU Lesser General Public License (LGPL)',
    keywords = ('test testing tools unittest fixtures setup teardown '
                'database stubs IO tempfile'),
    url = 'https://bitbucket.org/efreeze/sqlalchemy-fixture',
    
    packages = find_packages(),
    
    test_suite="fixture.setup_test_not_supported",
    entry_points = { 
        'console_scripts': [ 'fixture = fixture.command.generate:main' ] 
        },
    # the following allows e.g. easy_install fixture[django]
    extras_require = {
        'decorators': ['nose>=0.9.2'],
        'sqlalchemy': ['SQLAlchemy>=0.4'],
        },
    )
