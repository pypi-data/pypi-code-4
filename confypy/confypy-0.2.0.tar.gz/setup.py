#!/usr/bin/env python
import os
from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs(*f):
    return list(filter(None, [strip_comments(l) for l in open(
        os.path.join(os.getcwd(), 'requirements', *f)).readlines()]))

install_requires = reqs('default.txt')
tests_require = ['nose']

packages = [
    'confypy'
]

setup(
    name='confypy',
    version='0.2.0',
    description='Configuration Loading Utility',
    long_description=readme,
    author='Adam Venturella',
    author_email='aventurella@gmail.com',
    url='https://github.com/aventurella/confypy',
    license=license,
    packages=packages,
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    package_dir={'confypy': 'confypy'},
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ),
)
