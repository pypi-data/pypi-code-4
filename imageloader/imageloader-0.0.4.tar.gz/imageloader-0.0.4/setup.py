# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Extension
import inspect, os

filename = inspect.getfile(inspect.currentframe())
dirpath = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
long_description = open(os.path.join(dirpath, "README.rst")).read()


__author__  = "Hayaki Saito (user@zuse.jp)"
__version__ = "0.0.4"
__license__ = "GPL v3"

setup(name                  = 'imageloader',
      version               = __version__,
      description           = 'An image loader library which provides a subset of PIL interface.',
      long_description      = long_description,
      ext_modules           = [Extension('imageloader', sources = ['imageloader.c'])],
      classifiers           = ['Development Status :: 4 - Beta',
                               'Intended Audience :: Developers',
                               'License :: OSI Approved :: GNU General Public License (GPL)',
                               'Programming Language :: Python'
                               ],
      keywords              = 'image',
      author                = __author__,
      author_email          = 'user@zuse.jp',
      url                   = 'https://github.com/saitoha/python-imageloader',
      license               = __license__,
      zip_safe              = False,
      include_package_data  = True,
      )

