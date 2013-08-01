#!/usr/bin/env python

import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


README = read('README.markdown')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests', '-s']
        self.test_suite = True

    def run_tests(self):
        import pytest
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='django-modeltools',
    version='1.0.0',
    description='A collection of utilities that make dealing with Django models more fun.',
    url='https://github.com/hzdg/django-modeltools',
    long_description=README,
    packages=find_packages(),
    install_requires=[
        'enum34',
    ],
    tests_require=[
        'pytest-django',
        'Django',
    ],
    cmdclass={'test': PyTest},
)
