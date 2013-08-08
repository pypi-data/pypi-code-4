#!/usr/bin/env python

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


#Dependencies - python eggs
install_requires = [
        'Django >= 1.2.5', # main framework
        'lxml == 2.2.6', # XML processing library combining libxml2/libxslt with the ElementTree API
        'django-countries',
]


setup(name='django-smscoin',
    version='0.1',
    description='Django application to use sms processing system http://smscoin.com/',
    long_description=read('README.rst'),
    author='Arpaso',
    author_email='arvid@arpaso.com',
    url='https://github.com/Arpaso/smscoin',
    download_url='https://github.com/Arpaso/smscoin/tarball/0.1',
    include_package_data=True,    # include everything in source control
    zip_safe=False,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 3 - Alpha",
        'Environment :: Web Environment',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
    ],
    install_requires=install_requires,
)
