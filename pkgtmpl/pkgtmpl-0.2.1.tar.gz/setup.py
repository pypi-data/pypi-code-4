#!/usr/bin/env python
from __future__ import print_function
import codecs
import os
from pip.req import parse_requirements
from setuptools import setup


appname = 'pkgtmpl'
pkgname = appname.lower().replace('-', '_')

def read(fn):
    with codecs.open(fn, 'r', 'utf-8') as fh:
        contents = fh.read()
    return contents


setup(
    name=appname,
    version='0.2.1',
    description="Bootstrap python packages with sane defaults",
    long_description=read(os.path.join(os.path.dirname(__file__),
                                       'README.md')),
    packages=[pkgname],
    include_package_data=True,
    install_requires = [str(ir.req) for ir
                                    in parse_requirements('requirements.txt')],
    entry_points={
        'console_scripts': {
            'pkgtmpl = pkgtmpl:main',
        },
    },
    author='Jacob Magnusson',
    author_email='m@jacobian.se',
    url='https://github.com/jmagnusson/pkgtmpl',
    license='BSD',
    platforms=['unix', 'macos'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
    ],
)
