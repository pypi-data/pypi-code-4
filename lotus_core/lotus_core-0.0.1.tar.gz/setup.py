
from setuptools import setup, Extension, find_packages

module = Extension(
  "lotus_core_hpp",
  sources            = ["src/module_core.cpp"],
  include_dirs       = ["include_hpp","include_py","pint/include_hpp",
                        "/usr/include","/opt/local/include"],
  extra_compile_args = ["-w"],
  library_dirs       = ["/usr/lib","/opt/local/lib"],
  libraries          = ["boost_python"]
)

setup(
  name               = "lotus_core",
  version            = "0.0.1",
  packages           = find_packages(),
  package_data       = {"lotus_core":["basis_DATA/*.basis"]},
  ext_modules        = [module],
  author             = "T.Shimazaki, T.Abe, M.Hashimoto, and T.Maeda",
  author_email       = "t-shimazaki@riken.jp",
  license            = "MIT License",
  url                = "https://bitbucket.org/tshima/lotus_core",
  classifiers        = ["License :: OSI Approved :: MIT License",
                        "Operating System :: MacOS :: MacOS X", 
                        "Operating System :: POSIX :: Linux", 
                       ]
)



