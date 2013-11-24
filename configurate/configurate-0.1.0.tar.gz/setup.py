from __future__ import absolute_import

import os

from setuptools import setup

version = {}
with open(os.path.join(os.path.dirname(__file__), 'configurate', 'version.py')) as ver_file:
    # Avoiding "execfile" because Python 3 doesn't provide it.
    exec(compile(ver_file.read(), ver_file.name, 'exec'), version)
version = version['version']

setup(
    name='configurate',
    version=version,
    author='Mike Nerone',
    author_email='mike@nerone.org',
    url='https://github.com/mikenerone/configurate',
    description=(
        "A simple, but smart, dict-like configuration object that's not opinionated about the file format you prefer."
    ),
    long_description=open('README.rst').read(),
    license='ALv2',
    packages=['configurate'],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
    keywords=[
        'configuration',
        'configurate',
        'config',
        'dict',
        'attribute',
    ],
)
