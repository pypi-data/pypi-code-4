#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
Created on 25.07.2013

@author: rombr

Deploy:
setup.py sdist upload
'''
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


from distutils.command.install import INSTALL_SCHEMES
import os

def fullsplit(path, result=None):
    """
Split a pathname into components (the opposite of os.path.join) in a
platform-neutral way.
"""
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# Tell distutils not to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
src_dir = 'pynano'

for dirpath, dirnames, filenames in os.walk(src_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in (
                                                      '__pycache__',
                                                      'env',
                                                      )]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name="PyNanoCMS",
    version='0.2.5',
    url='https://github.com/rombr/pynano',
    author='Roman Bondar',
    author_email='rombr5@gmail.com',
    description='Static site generator',
    license="BSD",
    packages=packages,
    data_files=data_files,
    scripts=['pynano/pynano.py', ],
    install_requires=['jinja2'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
   ],
)
