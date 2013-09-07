#!/usr/bin/env python
import sys
import setuptools

requires = ["pylint"]

console_script = """
[console_scripts]
pylint-patcher = pylint_patcher.main:main
"""

# from pylint_patcher._version import __version__
exec(open("pylint_patcher/_version.py").read())

kw = {'entry_points': console_script,
      'zip_safe': True,
      'install_requires': requires
      }

setuptools.setup(name='pylint-patcher',
      version=__version__,
      description="Wrapper around Pylint to allow lint exceptions to be stored in a patchfile",
      long_description=open("README.rst").read(),
      author="Pete Burgers",
      url="https://github.com/sneakypete81/pylint-patcher",
      packages=["pylint_patcher"],
      keywords=["pylint-patcher", "pylint_patcher", "pylint",
                "patch", "patchfile"],
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Quality Assurance",
                   "Topic :: Utilities",
                   ],
      license="GPL 2.0",
      test_suite="tests",
      **kw
      )
