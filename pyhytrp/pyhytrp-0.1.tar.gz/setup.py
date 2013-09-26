#!/usr/bin/env python

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from distutils.core import setup

setup(name='pyhytrp',
    version='0.1',
    description='Python interface for configuring HYTRP serial devices by Canton Electronics',
    author='Matwey V. Kornilov',
    author_email='matwey.kornilov@gmail.com',
    url='https://bitbucket.org/matwey/pyhytrp',
    packages=['hytrp'],
    scripts=['hytrpctl.py'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Hardware',]
    )
