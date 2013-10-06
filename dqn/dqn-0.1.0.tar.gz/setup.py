#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, find_packages

ROOT = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(ROOT, 'README')

try:
    with open(README_PATH, 'rb') as fp:
        long_desc = fp.read()
except:
    long_desc = ''
    
requires = ['lxml',
            'mercurial',
            'sphinxcontrib-dqndomain',
            ]

setup(
    name='dqn',
    version='0.1.0',
    url='https://bitbucket.org/takesxi_sximada/dqn',
    download_url='https://bitbucket.org/takesxi_sximada/dqn',
    license='BSD',
    author='TakesxiSximada',
    author_email='takesxi.sximada@gmail.com',
    description='The dqn create ReST files for sphinx from source code',
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
    py_modules=['dqn'],
    include_package_data=True,
    install_requires=requires,
    #packages=find_packages(),
    #test_suite='nose.collector',
    #test_require=['Nose'],
    entry_points = """\
    [console_scripts]
    dqn = dqn:main
    """
)
