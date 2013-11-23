# Setup script for Ditz.

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup
import ditz

desc = """
This package is intended to be a drop-in replacement for the Ditz
distributed issue tracker.  It provides a command-line program, which acts
(mostly) the same way as Ditz, and it adds several other nice things too.
"""

setup(name             = ditz.__title__,
      author           = ditz.__author__,
      author_email     = ditz.__email__,
      description      = ditz.__doc__.strip(),
      long_description = desc.strip(),
      version          = ditz.__version__,
      license          = ditz.__license__,
      url              = ditz.__url__,
      classifiers      = ditz.__classifiers__.strip().split("\n"),

      packages = ["ditz"],

      install_requires = [
          'pyyaml >= 3.10',
      ],

      tests_require = [
          'nose >= 1.3.0',
          'coverage >= 3.6',
          'mock >= 1.0.1',
      ],

      test_suite = 'nose.collector',

      entry_points = {
          'console_scripts': [
              'pyditz = ditz.console:main'
          ]
      },

      zip_safe = True)
