#!/usr/bin/env python

# Copyright 2011 GRNET S.A. All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#   1. Redistributions of source code must retain the above
#      copyright notice, this list of conditions and the following
#      disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY GRNET S.A. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GRNET S.A OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be
# interpreted as representing official policies, either expressed
# or implied, of GRNET S.A.

from setuptools import setup
from sys import version_info
import collections

import kamaki


optional = ['ansicolors',
            'progress>=1.0.2']
requires = ['objpool']

if version_info < (2, 7):
    requires.append('argparse')

setup(
    name='kamaki',
    version=kamaki.__version__,
    description='A command-line tool for managing clouds',
    long_description=open('README.rst').read(),
    url='http://code.grnet.gr/projects/kamaki',
    license='BSD',
    author='Synnefo development team',
    author_email='synnefo-devel@googlegroups.com',
    maintainer='Synnefo development team',
    maintainer_email='synnefo-devel@googlegroups.com',
    packages=[
        'kamaki',
        'kamaki.cli',
        'kamaki.cli.commands',
        'kamaki.clients',
        'kamaki.clients.livetest',
        'kamaki.clients.connection',
        'kamaki.clients.commissioning',
        'kamaki.clients.quotaholder',
        'kamaki.clients.quotaholder.api',
        'kamaki.clients.commissioning.utils'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': ['kamaki = kamaki.cli:main']
    },
    install_requires=requires
)
