#!/usr/bin/env python
"""
django-casscache
~~~~~~~~~~~~~~~~

Django backend for python-casscache

:copyright: (c) 2013 by Matt Robenolt.
:license: BSD, see LICENSE for more details.
"""

from setuptools import setup, find_packages

setup(
    name='django-casscache',
    version='0.0.3',
    author='Matt Robenolt',
    author_email='matt@ydekproductions.com',
    url='https://github.com/mattrobenolt/django-casscache',
    description='Django backend for python-casscache',
    license='BSD',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'casscache==0.0.3',
    ],
    py_modules=['django_casscache'],
    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
