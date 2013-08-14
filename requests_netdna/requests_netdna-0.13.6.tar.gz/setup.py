#!/usr/bin/env python

import os
import sys

import requests_netdna
from requests_netdna.compat import is_py2

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

packages = [
    'requests_netdna',
    'requests_netdna.packages',
    'requests_netdna.packages.urllib3',
    'requests_netdna.packages.urllib3.packages',
    'requests_netdna.packages.urllib3.packages.ssl_match_hostname'
]

if is_py2:
    packages.extend([
        'requests_netdna.packages.oauthlib',
        'requests_netdna.packages.oauthlib.oauth1',
        'requests_netdna.packages.oauthlib.oauth1.rfc5849',
        'requests_netdna.packages.oauthlib.oauth2',
        'requests_netdna.packages.oauthlib.oauth2.draft25',
        'requests_netdna.packages.chardet',
    ])
else:
    packages.append('requests_netdna.packages.chardet2')

requires = ['requests']

setup(
    name='requests_netdna',
    version=requests_netdna.__version__,
    description='Python HTTP for Humans.',
    long_description=open('README.rst').read() + '\n\n' +
                     open('HISTORY.rst').read(),
    author='Kenneth Reitz',
    author_email='me@kennethreitz.com',
    url='http://python-requests.org',
    packages=packages,
    package_data={'': ['LICENSE', 'NOTICE'], 'requests': ['*.pem']},
    package_dir={'requests_netdna': 'requests_netdna'},
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE').read(),
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
    ),
)
