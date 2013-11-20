#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
setup(
    name='django_ffiler',
    version='0.1',
    packages=find_packages(),
    requires=['python (>= 2.5)', 'django (<= 1.5)'],
    description='Django admin inline images + multiupload. ',
    long_description=open('README.md').read(),
    author='Anton',
    author_email='thisice@gmail.com',
    url='https://github.com/xacce/django_ffiler',
    download_url='https://github.com/xacce/django_ffiler/archive/master.zip',
    license='MIT License',
    keywords=['django', 'multiupload', 'admin'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        ],
    )