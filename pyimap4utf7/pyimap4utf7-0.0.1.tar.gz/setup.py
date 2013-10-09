#!/usr/bin/python

from setuptools import setup, find_packages

version = '0.0.1'

setup(
    name='pyimap4utf7',
    version=version,
    author='danielblack',
    author_email='danielblack@danielblack.name',
    url='https://github.com/DanielBlack/pyimap4utf7',
    license='MIT',
    description='IMAP4 style UTF7 encoder/decoder in python',
    packages=find_packages(),
    zip_safe=False,
    keywords='imap4 utf7',
)
