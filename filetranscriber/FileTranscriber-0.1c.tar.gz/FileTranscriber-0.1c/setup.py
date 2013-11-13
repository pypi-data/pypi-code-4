# -*- coding: utf-8 -*-
from distutils.core import setup
import sys

def long_description():
    with open('README.md', 'r') as readme:
        readme_text = readme.read()
    return(readme_text)

setup(name='FileTranscriber',
      version='0.1c',
      description='''A small utility that simulates user typing to aid \
file transcription in limited environments''',
      long_description=long_description(),
      author='Paul Barton',
      author_email='pablo.barton@gmail.com',
      url='https://github.com/SavinaRoja/FileTranscriber',
      install_requires = ['docopt', 'PyUserInput'],
      license='http://opensource.org/licenses/MIT',
      scripts=['transcribe'])
