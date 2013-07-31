#!/usr/bin/env python3

from distutils.core import setup

import os

## relative_path = os.path.split(__file__)[0]
## readme_path = '{}{}{}'.format(
##     relative_path,
##     os.sep if relative_path else '',
##     'README.txt')
## with open(readme_path) as file:
##     long_description = file.read()

with open('README.txt') as file:
    long_description = file.read()

setup(name='ptTools',
      version='0.1.4',
      description='DSL for pattern matching on .py parse trees.',
      #url='http://github.com/941design',
      url='http://pypi.python.org/pypi/ptTools',
      author='Markus Rother',
      author_email='python@markusrother.de',
      license='GNU-GPL',
      long_description=long_description,
      platforms=['Linux'],
      #package_dir={'ptTools':'lib'},
      packages=[
          'ptTools',
          'ptTools.doc',
          'ptTools.doc.examples',
          'ptTools.examples',
          'ptTools.examples.pycat',
          'ptTools.examples.extract',
          'ptTools.examples.test',
          'ptTools.misc',
          'ptTools.parsetree',
          'ptTools.patterns',
          'ptTools.ptpatterns',
          'ptTools.test',
          'ptTools.test.misc',
          'ptTools.test.misc.acceptors',
          'ptTools.test.parsetree',
          'ptTools.test.patterns',
          'ptTools.test.ptpatterns',
          'ptTools.tokenizer',
          'ptTools.writers',
          ],
      classifiers=[
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: Unix',
          'Programming Language :: Python :: 3.2',
          'Topic :: Software Development',
          'Topic :: Software Development :: Code Generators',
          'Topic :: Software Development :: Compilers',
          'Topic :: Software Development :: Debuggers',
          'Topic :: Software Development :: Testing',
          'Topic :: Utilities',
          ],
      )
