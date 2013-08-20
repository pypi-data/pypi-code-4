#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages
from pip.req import parse_requirements
import re
import os

base_name = 'archer'
v_file = open(os.path.join(os.path.dirname(__file__),
                           base_name, '__init__.py'))

VERSION = re.compile(r".*__version__ = '(.*?)'",
                     re.S).match(v_file.read()).group(1)

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

requirements = [str(ir.req) for ir in parse_requirements('requirements/common.txt')]

setup(
    name='stfc_stratum_uploader',
    version=VERSION,
    author=u'Michal Knapik',
    author_email='Michael.Knapik@stfc.ac.uk',
    package_dir={base_name: base_name},
    packages=find_packages(exclude=["*.tests"]), # include all packages under this directory
    scripts=['manage-stfc-stratum-uploader.py'],
    include_package_data=True,
    url='git://github.com/mknapik/uploader.git',
    license='Apache License',
    description='Provides interface for uploading and distributing software through cvmfs repositories.',
    long_description=open('README.md').read,
    zip_safe=False,
    keywords=['cvmfs', 'django', 'uploader', 'vo', 'cern', 'stfc', 'ral'],
    # Adds dependencies
    install_requires=requirements,
    dependency_links=[
        # git fetching doesn't work for old pip versions
#        'git+https://github.com/mknapik/django-bootstrap-toolkit#egg=django-bootstrap-toolkit',
        'https://github.com/mknapik/uploader/archive/master.zip3egg=django-bootstrap-toolkit'
    ],
)
