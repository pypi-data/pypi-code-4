import sys
import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import twlogger


def read(filename):
    """Open a file and return its contents."""
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


def read_requirements(filename):
    """Open a requirements file and return list of its lines."""
    return read(filename).split('\n')


class PyTest(TestCommand):
    """Command to run unit tests after in-place build."""

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['tests']
        self.test_suite = True

    def run_tests(self):
        # Importing here, `cause outside the eggs aren't loaded.
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='TWLogger',
    version=twlogger.__version__,
    author='TaskWorkshop',
    author_email='contact@taskworkshop.com',
    description='Client for TaskWorkshop exceptions',
    long_description=read('README.rst'),
    url='https://github.com/TaskWorkshop/taskworkshop-logger-python',
    license=read('LICENSE'),
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=(
        'requests==1.2.0',
    ),
    tests_require=read_requirements('test_requirements.txt'),
    cmdclass={'test': PyTest},
    entry_points={
        'paste.filter_app_factory': [
            'twlogger = '
            'twlogger.middleware:make_middleware',
        ],
    })
