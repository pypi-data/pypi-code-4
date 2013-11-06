#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os
import subprocess
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


if int(sys.version[0]) < 3:
    reload(sys).setdefaultencoding('utf-8')


def read(*path):
    basepath = os.path.abspath(os.path.dirname(__file__))
    return codecs.open(os.path.join(basepath, *path), 'r', 'utf-8').read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


if sys.argv[-1] == 'publish':
    subprocess.call('python setup.py sdist upload', shell=True)
    sys.exit()


readme = read('README.rst')
changelog = read('CHANGELOG.rst').replace('.. :changelog:', '')


setup(
    name='timelog2csv',
    version='0.1.1',
    description='Converts a TimeLog calendar to a CSV file.',
    long_description=readme + '\n\n' + changelog,
    author=u'Markus Zapke-Gründemann',
    author_email='markus@keimlink.de',
    url='https://bitbucket.org/keimlink/timelog2csv',
    py_modules=['timelog2csv'],
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'docopt==0.6.1',
        'icalendar==3.5'
    ],
    license="BSD",
    zip_safe=False,
    keywords='timelog2csv timelog csv',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': ['timelog2csv = timelog2csv:main']
    },
    tests_require=[
        'pytest==2.4.2',
    ],
    cmdclass = {'test': PyTest},
)
