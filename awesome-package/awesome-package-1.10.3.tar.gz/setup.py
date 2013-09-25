#!/usr/bin/env python

from setuptools import setup, find_packages
from awesome import __version__

with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='awesome-package',
    version=__version__,
    description=('Integrates the awesomeness'),
    long_description=readme,
    author='Tim Heap',
    author_email='heap.tim@gmail.com',
    url='https://bitbucket.org/tim_heap/python-packaging-101',
    license='Unlicense',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],

    packages=find_packages(exclude=['tests']),
    package_data={ },
    include_package_data=True,
    zip_safe=False,
)
