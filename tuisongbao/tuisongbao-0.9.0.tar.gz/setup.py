#!/usr/bin/env python

from setuptools import setup

setup(
    name='tuisongbao',
    version='0.9.0',
    description='Tuisongbao SDK',
    author='www.tuisongbao.com',
    author_email='support@tuisongbao.com',
    maintainer='www.tuisongbao.com',
    url='https://github.com/tuisongbao/python-sdk',
    license='Apache',
    packages=['tuisongbao'],
    package_dir={'': 'lib'},
    install_requires=[
        'requests',
        'python-dateutil'
    ]
)
