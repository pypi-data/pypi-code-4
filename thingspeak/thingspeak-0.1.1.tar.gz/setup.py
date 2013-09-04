from __future__ import ( print_function, with_statement, absolute_import )
import sys

# When possible, use distribute_setup's version of tools
try:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
except ImportError:
    from setuptools import setup, find_packages
if sys.version >= '2.3':
  import re, os, sys
  version = re.search(
        r"__version__.*'(.+)'",
        open('thingspeak.py').read()).group(1)
else:
    raise Exception("only python 2.3 or newer supported")

setup(
    name='thingspeak',
    version= version,
    description='Client library for the thingspeak.com API',
    author='Daniel Bergey',
    author_email='bergey@alum.mit.edu',
    url='https://github.com/bergey/thingspeak',
    packages=find_packages(where='.'),
    py_modules=['thingspeak'],
    include_package_data=True,
    zip_safe=False,
)
