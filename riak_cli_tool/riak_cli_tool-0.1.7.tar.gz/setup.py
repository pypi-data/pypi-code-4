#!/usr/bin/env python

import riak_cli_tool
import glob
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = ['requests==1.0.4']

packages=['riak_cli_tool']

setup(
    name='riak_cli_tool',
    version=riak_cli_tool.__version__,
    description='Riak tool',
    long_description=open('README.rst').read(),
    author='Greg Moselle',
    author_email='greg.moselle@enstratius.com',
    url='https://pypi.python.org/pypi/riak_cli_tool',
    packages=packages,
    package_data={'': ['LICENSE', 'README.rst', 'requirements.txt']},
    package_dir={'riak_cli_tool': 'riak_cli_tool'},
    include_package_data=True,
    install_requires=requires,
		scripts=glob.glob(os.path.join('bin', '*')),
    license='Apache 2.0',
    zip_safe=False,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ),
)
