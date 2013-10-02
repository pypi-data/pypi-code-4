#!/usr/bin/python

from setuptools import setup, find_packages

archive = 'https://github.com/Elarnon/pygments-pvs/archive/'
version = '0.1'

setup(
    name = 'pygments-pvs',
    version = version,
    description = 'Pygments lexer for PVS source files',
    long_description = open('README.rst').read(),
    license = 'MIT',
    author = 'Basile Clement',
    author_email = 'basile@clement.pm',
    url = 'https://github.com/Elarnon/pygments-pvs',
    download_url = archive + version + '.tar.gz',
    packages = find_packages(),
    zip_safe = True,
    install_requires = [
        'pygments'
    ],
    entry_points = {
        'pygments.lexers': 'pvs=pygments_pvs.lexer:PVSLexer',
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
