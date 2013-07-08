#! /usr/bin/python
# coding=utf-8

__author__ = 'ajumell'

from distutils.core import setup

from distutils.command.install import INSTALL_SCHEMES
from distutils.command.install_data import install_data

import os
import sys


class osx_install_data(install_data):
    def finalize_options(self):
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)


if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}


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

project_dir = 'chinook'

for dirpath, dirnames, filenames in os.walk(project_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

# Small hack for working with bdist_wininst.
# See http://mail.python.org/pipermail/distutils-sig/2004-August/004134.html
if len(sys.argv) > 1 and sys.argv[1] == 'bdist_wininst':
    for file_info in data_files:
        file_info[0] = '\\PURELIB\\%s' % file_info[0]

setup(

    name='django-chinook',
    version='1.0.0',
    author=u'Muhammed K K',
    author_email='ajumell@gmail.com',

    url='https://bitbucket.org/xeoscript/django-chinook',
    description='A django app with models for chinook sample database and fixtures.',
    long_description=open('README.txt').read(),

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django'
    ],

    platforms=["any"],
    license="Freely Distributable",

    packages=packages,
    cmdclass=cmdclasses,
    data_files=data_files,

    install_requires=[
        "django",
    ]
)