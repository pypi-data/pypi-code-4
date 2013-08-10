#!/usr/bin/env python

# Setup script to install the PyBC generic blockchain library. Copied from the
# example distutils script.

from setuptools import setup

setup(name='pybc',
      version='0.4',
      description='Generic Blockchain Library',
      author='Adam Novak',
      author_email='interfect@gmail.com',
      url='https://bitbucket.org/interfect/pybc',
      packages=['pybc'],
      # We send a couple of server scripts along as examples.
      # We also have a coin GUI.
      scripts=['pybc_server', 'pybc_coinserver', 'pybc_cointk'],
      # We use Twisted for our p2p network, and pyelliptic for our coin
      # cryptography.
      install_requires=['twisted', 'pyelliptic', 'argparse'],
     )
