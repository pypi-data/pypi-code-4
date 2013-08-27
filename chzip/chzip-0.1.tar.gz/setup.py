#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup

# Post install command
# http://stackoverflow.com/a/1321345/753136
from distutils.command.install import install

import os
import distutils.sysconfig

class post_install(install):
    def run(self):
        install.run(self)

        res_dir = os.path.join(distutils.sysconfig.get_python_lib(), 'chzip', 'res')
        print('Downloading and installing the zip codes database to %s ...' % res_dir)
        import chzip
        chzip.download_and_unpack_all(res_dir)

setup(
    # Metadata
    name='chzip',
    version='0.1',
    description='Switzerland ZIP codes and town names',
    long_description="""
What is it?
===========

The chzip package provides a quick and easy Python interface to look for 
zip codes and cities in Switzerland.
    
Documentation
=============

Read the docs on `ReadTheDocs <http://chzip.readthedocs.org>`_ :-)
""",
    author='Mathieu Clément',
    author_email='mathieu.clement@freebourg.org',
    url='https://bitbucket.org/freebourg/chzip',
    classifiers=['Topic :: Communications', 
                 'Topic :: Office/Business',
                 'Programming Language :: Python :: 3',
                 'Operating System :: OS Independent',
                 'License :: OSI Approved :: BSD License',
                 'Intended Audience :: Customer Service',
                 'Intended Audience :: Telecommunications Industry'],
    license='BSD',

    # What's included
    packages=['chzip'],
    package_dir={'chzip': 'chzip'},
#    package_data={'chzip': ['test_resources']},

    # Post install command
    cmdclass={'install': post_install},
    )
