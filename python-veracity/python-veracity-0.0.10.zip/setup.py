#!/usr/bin/env python

"""
Setup script for python-veracity.
"""

import os
from setuptools import setup, Command

from veracity import __project__, TRACKING, POLLER, BUILDER


class TestCommand(Command):  # pylint: disable=R0904
    """Runs the unit and integration tests."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess
        raise SystemExit(subprocess.call([sys.executable, '-m',
                                          'unittest', 'discover']))

setup(
    name=__project__,
    version='0.0.10',

    description="Python wrapper for Veracity's command-line interface.",
    url='http://pypi.python.org/pypi/python-veracity',
    author='Jace Browning',
    author_email='jacebrowning@gmail.com',

    packages=['veracity', 'veracity.test'],
    package_data={'veracity': ['files/*'], 'veracity.test': ['files/*']},

    entry_points={'console_scripts': [TRACKING + ' = veracity.tracking:main',
                                      POLLER + ' = veracity.poller:main',
                                      BUILDER + ' = veracity.builder:main']},
    cmdclass={'test': TestCommand},

    install_requires=["pbs >= 0.110" if os.name == 'nt' else "sh >= 1.0.8",
                      "virtualenv >= 1.9.1"],
    long_description=open('README.rst').read(),
    license='LICENSE.txt',
)
