#!/usr/bin/env python
#
# Copyright 2013 Wantoto http://www.wantoto.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from distutils.core import setup
import fss
import os

setup(
    name='fss',
    description='Compile Flask/Jinja2 site into static html content',
    author='sodas tsai @ Wantoto',
    author_email='sodas@wantoto.com',
    url='https://bitbucket.org/wantoto/flask-static-site/',
    version=fss.__version__,
    packages=['fss'],
    license='Apache License Version 2.0',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    scripts=['fss/fss'],
    install_requires=[
        'Frozen-Flask>=0.5',
        'argh>=0.23',
        'argcomplete>=0.6',
    ],
)
