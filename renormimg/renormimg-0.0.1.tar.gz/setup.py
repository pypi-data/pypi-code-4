#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'renormimg',
    version = '0.0.1',
    author = 'Rich Wareham',
    author_email = 'rjw57@cantab.net',
    description = 'Renormalise a set of images on the command line',
    url = 'https://github.com/rjw57/renormimg',
    long_description = open('README.rst').read(),
    license = 'MIT',
    packages = find_packages(),
    entry_points = { 'console_scripts': [
        'renormimg = renormimg.tool:main',
    ] },
    install_requires = [ 'docopt', 'numpy', 'matplotlib', 'PIL', ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Utilities',
    ],
)

# vim:sw=4:sts=4:et

