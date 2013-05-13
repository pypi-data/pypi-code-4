# -*- encoding: utf-8 -*-

import os
import sys
import banco

from setuptools import setup, find_packages

if sys.version_info[:2] < (2, 6):
    raise RuntimeError('Requires Python 2.6 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

requires = [''
    'ginsfsm',
    'pyramid >= 1.4',
]

setup(
    name='banco',
    version=banco.__version__,
    description='banco',
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
    test_suite="banco.tests",
    entry_points="""\
    [paste.app_factory]
    main = banco.main:main
    pyramid_app = banco.main:pyramid_paste_factory
    """,
)
