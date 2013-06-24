#!/usr/bin/env python

# Support setuptools or distutils
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

# Version info -- read without importing
_locals = {}
with open('toothpick/_version.py') as fp:
    exec(fp.read(), None, _locals)
version = _locals['__version__']
from distutils.core import setup

setup(
    name='toothpick',
    version=version,
    description='Mapping documents to objects',
    license='BSD',
    long_description=open('README.markdown').read(),
    url='https://github.com/broadinstitute/toothpick',
    author='Andrew Roberts',
    author_email='adroberts@gmail.com',
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*"]),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=[
        "requests>1.0.0",
        "inflection",
        "werkzeug",
    ],
)

