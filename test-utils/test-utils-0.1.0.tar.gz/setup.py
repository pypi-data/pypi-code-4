import os
import sys

from setuptools import setup


def read_version_string():
    version = None
    current_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, current_dir)
    from test_utils import __version__
    version = __version__
    sys.path.pop(0)
    return version


setup(
    name='test-utils',
    version=read_version_string(),
    #long_description=open('README.rst').read() + '\n\n' +
    #open('CHANGES.rst').read(),
    packages=[
        'test_utils'
    ],
    package_dir={
        'test_utils': 'test_utils'
    },
    url='https://github.com/Kami/python-test-utils/',
    license='Apache License (2.0)',
    author='Tomaz Muraus',
    author_email='tomaz+pypi@tomaz.me',
    description='A collection of utility functions and classes which make' +
                'writing and running functional and integration tests easier.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
