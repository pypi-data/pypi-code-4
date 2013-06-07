#!/usr/bin/env python

from setuptools import setup, find_packages
#from setuptools.command.test import test as TestCommand

#class Tox(TestCommand):
#    def finalize_options(self):
#        TestCommand.finalize_options(self)
#        self.test_args = []
#        self.test_suite = True
#    def run_tests(self):
#        #import here, cause outside the eggs aren't loaded
#        import tox
#        errno = tox.cmdline(self.test_args)
#        sys.exit(errno)

DESCRIPTION = """
Ultralightweight python CLI framework
"""

setup(name='leip',
      version='0.0.8',
      description=DESCRIPTION,
      author='Mark Fiers',
      author_email='mark.fiers42@gmail.com',
      url='http://mfiers.github.com/Leip',
      packages=find_packages(),
      #tests_require = ['tox'],
      #cmdclass = {'test': Tox},
      requires=[
        'Yaco (>=0.1.11)',
        ],
      package_dir = {'Leip': 'leip'},
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          #'Programming Language :: Python :: 3',
          #'Programming Language :: Python :: 3.3',
          ]

     )
