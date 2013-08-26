#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='django_antimat',
    version='1.0.1',
    description='Django antimat is application for filtering swear words.',
    license='BSD',
    url='https://github.com/ruscoder/django_antimat',
    author='Vadim',
    author_email='Vadim <rusmiligamer@gmail.com>',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
            'Django>=1.4.3',
            'south',
            'pymorphy>=0.5.6',
            ],
    keywords='django antimat anti snub antiswear swear words',
)
