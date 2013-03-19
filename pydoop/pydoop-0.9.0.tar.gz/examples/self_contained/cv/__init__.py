# BEGIN_COPYRIGHT
# 
# Copyright 2009-2013 CRS4.
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
# 
# END_COPYRIGHT

"""
A trivial MapReduce application that counts the occurence of each
vowel in a text input stream. It is more structured than would be
necessary because we want to test automatic distribution of a package
rather than a single module.
"""

# NOTE: some of the variables defined here are
# parsed by setup.py, check it before modifying them.

__version__ = "0.1"
__author__ = "Simone Leo, Gianluigi Zanetti, Luca Pireddu"
__author_email__ = "<simone.leo@crs4.it>, <gianluigi.zanetti@crs4.it>, <luca.pireddu@crs4.it>"
__url__ = "http://pydoop.sourceforge.net"
