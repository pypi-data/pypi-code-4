#!/usr/bin/env python

# Copyright 2013 Andrew Mussey. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''A tool for importing *.cql files into a Cassandra database

cassandra-cql is a Python-based tool for importing CQL3 *.cql
files into Cassandra databases (much in the same way you can use
mysql to import *.sql files).'''

from distutils.core import setup

doclines = __doc__.split("\n")

setup(
    name='cassandra-cql',
    version='0.9.0',
    description=doclines[0],
    long_description="\n".join(doclines[2:]),
    keywords='python cql cassandra',
    author='Andrew Mussey',
    author_email='admin@ajama.org',
    url='https://github.com/amussey/cassandra-cql',
    platforms=["any"],
    license="http://www.apache.org/licenses/LICENSE-2.0",
    install_requires=["cql"],
    packages=['cassandra_cql'],
    scripts=['cassandra-cql']
)
