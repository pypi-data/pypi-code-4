#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name             = 'convert-to-redirects',
    version          = '0.1.3',
    packages         = find_packages(),
    requires         = ['python (>= 2.7)', 'docopt (>= 0.6)'],
    install_requires =['docopt==0.6'],
    description      = 'Convert urls list to nginx or apache redirects.',
    long_description = open('README.markdown').read(),
    author           = 'Kovardin Artem',
    author_email     = 'horechek@gmail.com',
    url              = 'https://github.com/horechek/convert-to-redirects',
    download_url     = 'https://github.com/horechek/convert-to-redirects/tarball/master',
    license          = 'MIT License',
    keywords         = 'redirects, nginx, apache',
    classifiers      = [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
    entry_points     = {
        'console_scripts':
            ['redirects = redirects.redirects:console_command']
        }
)
