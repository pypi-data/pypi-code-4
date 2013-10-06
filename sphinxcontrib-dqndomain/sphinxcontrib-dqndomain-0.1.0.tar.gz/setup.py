#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import os

ROOT = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(ROOT, 'README')

try:
    with open(README_PATH, 'rb') as fp:
        long_desc = fp.read()
except:
    pass
    
requires = ['Sphinx>=0.6']

setup(
    name='sphinxcontrib-dqndomain',
    version='0.1.0',
    url='https://bitbucket.org/takesxi_sximada/sphinxcontrib-dqndomain',
    download_url='https://bitbucket.org/takesxi_sximada/sphinxcontrib-dqndomain',
    license='BSD',
    author='TakesxiSximada',
    author_email='takesxi.sximada@gmail.com',
    description='Sphinx dqn extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
