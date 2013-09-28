from setuptools import setup
from distutils.core import Command
import os
import sys

class TestCommand(Command):
    description = "Run tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call(['nosetests', '--debug=DEBUG', '-s'])
        raise SystemExit(errno)

setup(
    name='mafan_traditional',
    version='1.0.0',
    author='Herman Schaaf',
    author_email='herman@ironzebra.com',
    packages=['mafan_traditional'],
    scripts=[],
    url='https://github.com/hermanschaaf/mafan_traditional',
    license='LICENSE.txt',
    description='A traditional dictionary for use with Mafan',
    long_description=open('README.md').read(),
    cmdclass={
        'test': TestCommand,
    },
    install_requires=[
    ],
)