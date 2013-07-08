#!/usr/bin/env python

from setuptools import setup, find_packages
import tmpbrowse
import os


def read(*names):
    values = dict()
    extensions = ['.txt', '.rst']
    for name in names:
        value = ''
        for extension in extensions:
            filename = name + extension
            if os.path.isfile(filename):
                value = open(name + extension).read()
                break
        values[name] = value
    return values

long_description = """
%(README)s

CHANGELOG
=========

%(CHANGES)s

""" % read('README', 'CHANGES')

setup(
    name='tmpbrowse',
    version=tmpbrowse.__version__,
    description='Spawns a temporary browser session for testing with your app development ',
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing",
    ],
    keywords='tmpbrowse browser chrome session test web development',
    author='Chakib Benziane',
    author_email='chakib.benz@gmail.com',
    maintainer='Chakib Benziane',
    maintainer_email='chakib.benz@gmail.com',
    url='https://github.com/sp4ke/tmpbrowse',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tmpbrowse = tmpbrowse.tmpbrowse:cli_run',
        ]
    },
)
