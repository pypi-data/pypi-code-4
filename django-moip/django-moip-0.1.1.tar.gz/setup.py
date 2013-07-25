#!/usr/bin/env python

from setuptools import setup, find_packages

import django_moip

version = ".".join(map(str, django_moip.__version__))
print 'Version:', version

setup(
    name='django-moip',
    version=version,
    author='Alan Justino da Silva',
    author_email='alan.justino@yahoo.com.br',
    url='http://github.com/alanjds/django-moip',
    download_url='https://github.com/alanjds/django-moip/tarball/'+version,
    install_requires=[
        'Django>=1.0',
        'furl',
    ],
    tests_require = [
        'django-discover-runner'
    ],
    test_suite = 'runtests.runtests',
    description = 'A pluggable Django application for integrating MoIP HTML (for now)',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
