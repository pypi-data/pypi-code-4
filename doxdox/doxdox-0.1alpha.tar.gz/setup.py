#!/usr/bin/python

from setuptools import setup

setup(
    name='doxdox',
    version='0.1alpha',
    description='A simple documentation generator that takes output from dox and builds a Bootstrap based documentation file.',
    author='Scott Doxey',
    url='https://github.com/neogeek/doxdox',
    packages=['doxdox'],
    scripts=['doxdox/doxdox.py'],
    install_requires=[
        'Jinja2==2.7.1',
        'Pygments==1.6',
        'sh==1.09'
    ]
)