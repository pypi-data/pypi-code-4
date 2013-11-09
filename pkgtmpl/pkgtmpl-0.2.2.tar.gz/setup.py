#!/usr/bin/env python
"""
pkgtmpl
-------

Bootstrap python packages with sane defaults

Features include:

- Generates .gitignore, AUTHORS, CHANGELOG,
  LICENSE (BSD simplified by default), MANIFEST.in, README.md,
  requirements.txt, setup.py, tests.py and tox.ini.

- Sets your name, github username, package name in the templates by
  reading a config that should be located @ ~/.config/pkgtmpl.ini.

- Optional: Add Travis CI status and twitter account to the readme

- Sets your name and year in the copyright notice of the license file

"""
from __future__ import print_function
from pip.req import parse_requirements
from setuptools import setup


appname = 'pkgtmpl'
pkgname = appname.lower().replace('-', '_')
metadata_relpath = '{}/metadata.py'.format(pkgname)

# Get package metadata. We use exec here instead of importing the
# package directly, so we can avoid any potential import errors.
with open(metadata_relpath) as fh:
    metadata = {}
    exec(fh.read(), globals(), metadata)


setup(
    name=appname,
    version=metadata['__version__'],
    description="Bootstrap python packages with sane defaults",
    long_description=__doc__,
    packages=[pkgname],
    include_package_data=True,
    install_requires = [str(ir.req) for ir
                                    in parse_requirements('requirements.txt')],
    entry_points={
        'console_scripts': {
            'pkgtmpl = pkgtmpl:main',
        },
    },
    author='Jacob Magnusson',
    author_email='m@jacobian.se',
    url='https://github.com/jmagnusson/pkgtmpl',
    license='BSD',
    platforms=['unix', 'macos'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
    ],
)
