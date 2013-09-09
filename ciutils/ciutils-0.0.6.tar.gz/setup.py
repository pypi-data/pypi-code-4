
r"""Helpers to use in CI environments (e.g. use xmlrunner with `test` command)

What's new in version 0.0.6
---------------------------

- Patch xmlrunner to support skipped test cases in python=2.6

What's new in version 0.0.3
---------------------------

- Added support in Linux (Unix ?) to look up free 
  TCP ports to be used during test runs.

What's new in version 0.0.2
---------------------------

- Helper function junitrunner configures the runner's 
  XML output folder using process' environment variables.

"""

from setuptools import setup

setup(name="ciutils",
      description=__doc__.split('\n', 1)[0],
      long_description=__doc__,
      author="Olemis Lang",
      author_email="olemis+py@gmail.com",
      version="0.0.6",
      install_requires=['unittest-xml-reporting'],
      py_modules=['ciutils'])

