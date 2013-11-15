
from setuptools import setup, Extension, find_packages
import sys
import os

try:
  import lotus_core
  print "----- import lotus_core -----"
  path_lotus_core = os.path.dirname(lotus_core.__file__)
  print "  path_lotus_core: ",path_lotus_core
except:
  print "----- lotus_core module -----"

requires = [
  "lotus_core",
]


setup(
  name               = "lotus",
  version            = "0.0.2",
  packages           = find_packages(),
  author             = "T.Shimazaki",
  author_email       = "t-shimazaki@riken.jp",
  license            = "MIT License",
  url                = "https://bitbucket.org/tshima/lotus",
  classifiers        = ["License :: OSI Approved :: MIT License",
                        "Operating System :: MacOS :: MacOS X", 
                        "Operating System :: POSIX :: Linux", 
                       ],
  install_requires  = requires,
)



