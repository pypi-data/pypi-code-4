# -*- encoding: utf-8 -*-

import os
import sys
import financiera

from setuptools import setup, find_packages

if sys.version_info[:2] < (2, 6):
    raise RuntimeError('Requires Python 2.6 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

requires = ['ginsfsm']

setup(name='financiera',
    version=financiera.__version__,
    description='financiera',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
    ],
    author='',
    author_email='',
    url='',
    license='MIT License',
    keywords='gobj ginsfsm finite state machine fsm wsgi',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="financiera.tests",
    entry_points="""\
    [paste.app_factory]
    main = financiera.main:main
    """,
)
