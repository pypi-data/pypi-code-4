# -*- encoding: utf-8 -*-

import os
import sys

from setuptools import setup, find_packages

if sys.version_info[:2] < (2, 6):
    raise RuntimeError('Requires Python 2.6 or better')

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

from ghtml import __version__

requires = ['ginsfsm', 'mako']

setup(name='ghtml',
    version=__version__,
    description='A gobj that generates html.',
    long_description=README + '\n\n',  # + CHANGES,
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
    ],
    author='ginsmar',
    author_email='ginsmar at artgins.com',
    url='https://bitbucket.org/artgins/ghtml',
    license='MIT License',
    keywords='gobj ginsfsm finite state machine fsm html5 css js',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=[],
    test_suite="ghtml.tests",
    entry_points="""\
    """,
)
