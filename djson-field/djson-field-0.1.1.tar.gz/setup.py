# -*- coding: utf-8 -*-

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djson-field',
    version='0.1.1',
    packages=['djson_field'],
    install_requires=[
        'django>=1.4.5'
    ],
    include_package_data=True,
    license='BSD License',
    description='A simple Django app to conduct Web-based polls.',
    long_description=README,
    url='http://djson-field.beslave.net/',
    author='Vladislav Lozhechnik',
    author_email='lozhechnik.vladislav@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
