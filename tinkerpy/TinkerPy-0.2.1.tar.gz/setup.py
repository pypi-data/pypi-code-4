from setuptools import setup, find_packages
import sys, os

version = '0.2.1'

setup(name='TinkerPy',
      version=version,
      description="Tools tinkering with basic Python stuff.",
      long_description='''\
      This Python 2 and 3 project (tested with 2.7 and 3.3) contains the
      package ``tinkerpy`` which provides:

      *   funtionality related to Python 2 versus 3
      *   special dictionary implementations
      *   a function to flatten data structures composed of iterables
      *   some useful decorators
      *   SAX handlers
      ''',
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Topic :: Software Development :: Libraries :: Python Modules'
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='tool decorator dict mapping Unicode',
      author='Michael Pohl',
      author_email='pohl-michael@gmx.biz',
      url='https://github.com/IvIePhisto/TinkerPy',
      license='MIT License',
      packages=find_packages(exclude=['tests']),
      test_suite='tests.test_suite',
      include_package_data=True,
      zip_safe=True,
)
