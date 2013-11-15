#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Elie Khoury <elie.khoury@idiap.ch>
# Thu Nov 14 22:20:38 CET 2013

"""Audio reader and writer using sox for bob and python
"""

from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires='xbob.extension'))
from xbob.extension import Extension, build_ext

setup(

    name="xbob.sox",
    version="1.0.0",
    description="Audio reader and writer using sox for bob and python",
    license="GPLv3",
    author='Elie Khoury',
    author_email='elie.khoury@idiap.ch',
    long_description=open('README.rst').read(),
    url='http://pypi.python.org/pypi/xbob.sox',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    namespace_packages=[
      "xbob",
      ],

    install_requires=[
      'setuptools',
      'bob',
      ],

    entry_points = {
      'console_scripts': [
        ],
      },

    cmdclass = {
      'build_ext': build_ext,
      },

    ext_modules=[
      Extension("xbob.sox._ext", #new implementation
        [
          "xbob/sox/ext/ext.cc",
          "xbob/sox/ext/reader.cc",
          "xbob/sox/ext/writer.cc",
          "xbob/sox/ext/utilities.cc",
        ],
        pkgconfig = [
          "sox",
        ],
        ),
      ],

    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],

    )
