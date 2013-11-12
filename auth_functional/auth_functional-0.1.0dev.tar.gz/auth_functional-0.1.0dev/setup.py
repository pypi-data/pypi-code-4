# -*- coding: utf-8 -*-
"Functional library for working with authentication and authorization in django"
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))

version = '0.1.0'
url = "http://github.com/ikame/django-auth-functional"

try:
    README = open(os.path.join(here, "README.rst")).read()
    README += open(os.path.join(here, "HISTORY.rst")).read()
except IOError:
    README = url


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(name='auth_functional',
      version=version,
      description=__doc__,
      long_description=README,
      keywords='django auth authentication authorization decorator functional',
      author='ikame',
      author_email='anler86@gmail.com',
      url=url,
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      tests_require=["pytest", "mock", "tox"],
      cmdclass={"test": PyTest},
      classifiers=[
          "Environment :: Plugins",
          "Environment :: Web Environment",
          "Framework :: Django",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.2",
          "Topic :: Internet :: WWW/HTTP",
      ])
