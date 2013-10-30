
from setuptools import setup, Extension, find_packages

requires = [
  "lotus_core",
]


setup(
  name               = "lotus",
  version            = "0.0.1",
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



