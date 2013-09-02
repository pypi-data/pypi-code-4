#!/usr/bin/python

import setuptools


setuptools.setup(
    name='nt_version',
    version='1.0.0',
    description='Version reporter for Openstack',
    author='NetEase Cloud',
    author_email='nvs@corp.netease.com',
    packages=setuptools.find_packages(exclude=['bin']),
    include_package_data=True,
    entry_points={
        'paste.app_factory': [
            'main=nt_version:app_factory'
        ],
        'paste.filter_factory': [
            'main=nt_version:filter_factory'
        ],
    },
    py_modules=[]
)
