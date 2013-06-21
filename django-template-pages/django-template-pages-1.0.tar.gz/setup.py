#!/usr/bin/env python

from distutils.core import setup

setup(name='django-template-pages',
    version='1.0',
    description='Flat pages based on template directory structure for django.',
    author='Leszek Piatek',
    author_email='lpiatek@gmail.com',
    url='https://github.com/iRynek/django-template-pages/',
    license='GPL',
    packages=[
        'template_pages',
        'template_pages.tests',
    ],
    requires=[
        'Django',
    ],
)
