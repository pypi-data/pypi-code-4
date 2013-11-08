#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

setup(
    name='djangocms-angular-compendium',
    version='0.1.0',
    description='Template overrides for DjangoCMS plugins when used with AngularJS',
    author='Jacob Rief',
    author_email='jacob.rief@gmail.com',
    url='https://github.com/jrief/djangocms-angular-compedium',
    packages=['angularjs_compendium'],
    install_requires=[],
    license='LICENSE-MIT',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    long_description=open('README.md').read(),
    include_package_data=True,
    zip_safe=False
)
