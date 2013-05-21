#!/usr/bin/env python

from distutils.core import setup
from lib import __version__

setup(name = 'ipa-zounds',
      version = __version__,
      description = 'IPA Zounds sound change applier',
      long_description = """The IPA Zounds application models language sound change by applying a given set of sound change rules to a given lexicon. It has a built-in model of the IPA, allowing users to write input words in IPA characters, and rules using those characters and/or the distinctive features of the model.""",
      author = 'Jamie Norrish',
      author_email = 'jamie@artefact.org.nz',
      url = 'http://zounds.artefact.org.nz/',
      license = 'GPL',
      platforms = ['GNU/Linux', 'MS Windows', 'Mac OS X'],
      classifiers = ['Development Status :: 5 - Production/Stable',
                     'Environment :: Console',
                     'Environment :: Win32 (MS Windows)',
                     'Environment :: X11 Applications :: GTK',
                     'Intended Audience :: End Users/Desktop',
                     'License :: OSI Approved :: GNU General Public License (GPL)',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Text Processing :: Linguistic'
                     ],
      package_dir = {'ipazounds': 'lib'},
      packages = ['ipazounds'],
      scripts = ['scripts/ipa.py', 'scripts/zounds.py',
                 'scripts/ipa-zounds.py'],
      )

