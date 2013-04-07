#!/usr/bin/env python

def configuration(parent_package='',top_path=None):
    from numpy.distutils.misc_util import Configuration
    config = Configuration('testing',parent_package,top_path)
    return config

if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(maintainer = "NumPy Developers",
          maintainer_email = "numpy-dev@numpy.org",
          description = "NumPy test module",
          url = "http://www.numpy.org",
          license = "NumPy License (BSD Style)",
          configuration = configuration,
          )
