#!/usr/bin/python
"""
Clover is a build tool that dynamically compiles JavaScript and Closure Template code. 


Features
########

  * Simplifies development with the closure compiler, library and templates.
  * Compiles javascript and soy templates on the fly
  * Closure unit testing framework support
  * Command line and web based test runners.
    * Selenium support to run tests in various drivers. 
  * Javascript internationalization support
  * Sourcemap support
  * Displays closure warnings and errors to the browsers console log.
  * Allows a single configuration file defining the entire compilation; replacing build scripts/etc.

"""
from setuptools import setup, find_packages
import os


def main():
    setup(**SETUP_KWARGS)
    
__dir__ = os.path.dirname(os.path.abspath(__file__))

with open('requirements.txt') as f:
    required = f.read().splitlines()

    
SETUP_KWARGS = {
    'name': 'clover',
    'version': '0.2',
    'description': __doc__,
    'author': 'Nate Skulic',
    'author_email': 'nate.skulic@gmail.com',
    'url': 'https://code.google.com/p/clover/',
    'packages': find_packages(),
    'zip_safe' : False,
    'package_dir':{'clover': 'clover'},
    "include_package_data": True,
    "install_requires": ['JPype1', 'nose', 'PyYAML', 'selenium', 'coverage', 'jinja2', 'WebOb', 'Paste', 'webapp2', 'cherrypy', 'py4j', 'polib'],
    "dependency_links" : [
        'http://github.com/originell/jpype/tarball/master#egg=jpype-1.0'
    ],
    "package_data":{
      'clover': [
          'javascript/**/*.js',
          'jars/*.jar'
      ],
    },
    "entry_points":'''
    [console_scripts]
    clover = clover.main:main
    '''
}

if __name__ == '__main__':
    main()
