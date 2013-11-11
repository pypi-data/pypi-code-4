#!/usr/bin/env python

import os

try:
    from setuptools.core import setup
    from setuptools.command.install import INSTALL_SCHEMES
except ImportError:
    from distutils.core import setup
    from distutils.command.install import INSTALL_SCHEMES

dependencies = ['motor', 'tornado']

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


packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
django_dir = 'ramen'

for dirpath, dirnames, filenames in os.walk(django_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])


setup(
    name='ramen',
    version='0.0.2',
    description="Tornado based simple web framework",
    long_description=open('README.md').read(),
    author='Anton Gorskiy',
    author_email='gorskiy.anton@gmail.com',
    url='http://gorskiy.kz/ramen',
    packages=packages,
    data_files=data_files,
    license='Apache v2',
    install_requires=dependencies,
    scripts = ['ramen/bin/ramen'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers'
    ]
)
