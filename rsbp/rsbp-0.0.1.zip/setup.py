import sys
import os

from setuptools import setup, find_packages

version = '0.0.1'
long_description = open('README.rst').read() + '\n\n' + open('CHANGES.rst').read()

setup(
    name='rsbp',
    version=version,
    description='Really Simple Blogging Platform, written in Django',
    long_description=long_description,
    keywords='django blog',
    author='Alex Holmes',
    author_email='alex@alex-holmes.com',
    url='https://github.com/alex2/rsbp',
    license='WTFPL',
    packages=['rsbp',],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'Django>=1.5',
        'Pillow',
        'South',
        'django-ckeditor>=4',
        'pytz',
    ],
)
