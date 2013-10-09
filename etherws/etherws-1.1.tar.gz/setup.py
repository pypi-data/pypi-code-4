#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# ===========================================================================
# Copyright (c) 2012-2013, Atzm WATANABE <atzm@atzm.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ===========================================================================
#
# $Id: setup.py 261 2013-10-09 17:07:31Z atzm $

import os
from setuptools import setup

longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='etherws',
    version='1.1',
    description='Ethernet over WebSocket',
    long_description=longdesc,
    author='Atzm WATANABE',
    author_email='atzm@atzm.org',
    license='BSD-2',
    entry_points={'console_scripts': ['etherws = etherws:_main']},
    py_modules=['etherws'],
    keywords=['http', 'websocket', 'ethernet', 'network'],
    platforms=['Linux'],
    install_requires=[
        'python-pytun>=0.2',
        'websocket-client>=0.7.0',
        'tornado>=2.3',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
    ],
)
