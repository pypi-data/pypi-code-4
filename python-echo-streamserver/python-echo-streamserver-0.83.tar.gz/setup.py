#! /usr/bin/env python
#
# Echo StreamServer API Client for Python
# ======================================================================
# Build distutils packages
# ======================================================================
# See Configuration: ./setup.cfg
#
# RPM Spec can't find the right python interpreter w/o help.
# So, bdist_rpm needs some extra parameters.
#
#% ./setup.py bdist_rpm --python='/usr/bin/python2.6'
# ======================================================================
try:
    # Allow Python eggs cmd: bdist_egg
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from echo import __version__

readme = open('README.rst', 'r')
README_TEXT = readme.read()
readme.close()

setup(name='python-echo-streamserver',
      version=__version__,
      license='PSF Licensed',
      description='Echo StreamServer API Client',
      long_description=README_TEXT,
      author='Andrew Droffner',
      author_email='adroffner@gmail.com',
      url='http://code.google.com/p/python-echo-streamserver/',
      download_url='https://code.google.com/p/python-echo-streamserver/downloads/list',
      packages=['echo', 'echo.feeds', 'echo.items', 'echo.eql'],
      scripts=['scripts/eql_shell'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Python Software Foundation License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          ],
     )

