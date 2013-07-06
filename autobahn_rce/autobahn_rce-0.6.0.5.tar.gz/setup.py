#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     setup.py
#
#     This file was originally created for RoboEearth
#     http://www.roboearth.org/
#
#     The research leading to these results has received funding from
#     the European Union Seventh Framework Programme FP7/2007-2013 under
#     grant agreement no248942 RoboEarth.
#
#     Copyright 2013 RoboEarth
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
#     \author/s: Dhananjay Sathe, Dominique Hunziker
#
#

from setuptools import setup, Extension

LONGSDESC = """
Twisted-based WebSocket/WAMP client and server framework.
Modified and optimised for the RoboEarth Cloud Engine

AutobahnPython provides a WebSocket (RFC6455, Hybi-10 to -17, Hixie-76)
framework for creating WebSocket-based clients and servers.

AutobahnPython also includes an implementation of WAMP
(The WebSockets Application Messaging Protocol), a light-weight,
asynchronous RPC/PubSub over JSON/WebSocket protocol.

More information:

   * http://autobahn.ws/python
   * http://wamp.ws

Source Code:

   * https://github.com/IDSCETHZurich/autobahn_rce
"""

## get version string from "autobahn/_version.py"
## See: http://stackoverflow.com/a/7071358/884770
##
import re
VERSIONFILE="autobahn/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
   verstr = mo.group(1)
else:
   raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

ext_modules = [
    Extension('autobahn.utf8validator', ['src/utf8validator.c']),
    Extension('autobahn.xormasker', ['src/xormasker.c']),
    ]

setup (
   name = 'autobahn_rce',
   version = verstr,
   description = 'AutobahnPython - Optimised and modified for the RoboEarth Cloud Engine.',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'Dhananjay Sathe',
   author_email = 'dhananjaysathe@gmail.com',
   url = 'https://github.com/IDSCETHZurich/autobahn_rce',
   platforms = ('Any'),
   install_requires = ['setuptools', 'Twisted>=11.1'],
   packages = ['autobahn'],
   ext_modules=ext_modules,
   zip_safe = False,
   classifiers = ["License :: OSI Approved :: Apache Software License",
                  "Development Status :: 5 - Production/Stable",
                  "Environment :: Console",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Topic :: Internet",
                  "Topic :: Software Development :: Libraries"],
   keywords = 'autobahn robotics cloud roboearth rapyuta autobahn.ws websocket realtime rfc6455 wamp rpc pubsub'
)
