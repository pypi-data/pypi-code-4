#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name='yt.formula.node',
      version='0.0.2',
      description='A sprinter formula installing node.js',
      long_description=open('README.rst').read(),
      author='Yusuke Tsutsumi',
      author_email='yusuke@yusuketsutsumi.com',
      url='http://github.com/toumorokoshi/yt.formula.node',
      packages=['yt', 'yt.formula'],
      install_requires=['sprinter>=1.1.1'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Topic :: System :: Software Distribution',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3'
      ],
      entry_points={},
      tests_require=['mock>=1.0.1', 'nose>=1.3.0', 'httpretty>=0.6.1'],
      test_suite='nose.collector'
)
