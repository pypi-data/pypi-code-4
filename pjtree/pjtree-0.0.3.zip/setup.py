# -*- utf-8 -*-


from setuptools import setup

NAME = 'pjtree'

VERSION = '0.0.3'

DESCRIPTION = 'Create files script.'

LONG_DESCRIPTION = """
Make any directory and files by json.
Make directory hierarchy to json.


Requirements
------------
* Python 2.7
* Python 3.3


Features
--------
* nonthing


Commands
--------
* jread
* jwrite


Examples
--------
Target directory to json.
::

    $ jread [Target directory] [-f, --file] [--encoding]

Make any directory and files by json.
::

    $ jwrite [Json] [Make path] [--encoding] [--force] [--notoverwrite]

Make any directory and files.


Installation
------------
easy_install:
::

    $ easy_install pjtree

pip:
::

    $ pip install pjtree


License
-------
Copyright (c) 2013, Kazuki Hasegawa All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


History
-------
Version 0.0.2 (7-11-2013)

* Responded to the python3.3.


Version 0.0.1 (7-9-2013)

* First release

"""

CLASSIFIERS = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Operating System :: OS Independent',
    'Development Status :: 2 - Pre-Alpha',
    'License :: OSI Approved :: BSD License'
]

PACKAGES = ['jread', 'jwrite']

AUTHOR = 'Kazuki Hasegawa'

MAIL_ADDRESS = 'hasegawa_0204@hotmail.co.jp'

URL = 'https://github.com/corrupt952/pjtree'

LICENSE = 'BSD'

ENTRY_POINTS = """
[console_scripts]
jread = jread.main:main
jwrite = jwrite.main:main
"""

REQUIRES = [
]

KEYWORDS = [
    'Json',
    'File'
]

setup(name=NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      classifiers=CLASSIFIERS,
      packages=PACKAGES,
      author=AUTHOR,
      author_email=MAIL_ADDRESS,
      url=URL,
      license=LICENSE,
      entry_points=ENTRY_POINTS,
      install_requires=REQUIRES
      )

