
from setuptools import setup, Extension, find_packages
import sys
import os

from distutils import sysconfig
import subprocess 

sys.path.append("./lotus_core")
sys.path.append("./tests_py")


def compile_python4lotus():
  pyver = sysconfig.get_config_var('VERSION')
  getvar = sysconfig.get_config_var
  flags = ['-I' + sysconfig.get_python_inc(),
           '-I' + sysconfig.get_python_inc(plat_specific=True)]
  libs = getvar('LIBS').split() + getvar('SYSLIBS').split()
  libs.append('-lpython'+pyver)

  str_flags = " ".join(flags)
  str_libs  = " ".join(libs)

  cmd_CC  ="gcc"
  cmd_CXX ="g++"
  if "CC"  in os.environ:  cmd_CC  = os.environ["CC"]
  if "CXX" in os.environ:  cmd_CXX = os.environ["CXX"]
  cmd=cmd_CXX+" "+str_flags+" -o bin/python4lotus src/main_python4lotus.cpp "+str_libs
  print "===== compile python4lotus ====="
  print "\n",cmd,"\n"
  if os.path.exists("bin/python4lotus")==True: os.remove("bin/python4lotus")
  if os.path.exists("bin")==False: os.mkdir("bin")
  subprocess.call(cmd.split())


compile_python4lotus()

module = Extension(
  "lotus_core_hpp",
  sources            = ["src/module_core.cpp"],
  include_dirs       = ["include_hpp","include_py","pint/include_hpp"],
  extra_compile_args = ["-w"],
  libraries          = ["boost_python"]
)

setup(
  name               = "lotus_core",
  version            = "0.0.4",
  packages           = find_packages(),
  package_data       = {"lotus_core":["basis_DATA/*.basis"]},
  ext_modules        = [module],
  scripts            = ["bin/python4lotus"],
  author             = "T.Shimazaki, T.Abe, M.Hashimoto, and T.Maeda",
  author_email       = "t-shimazaki@riken.jp",
  license            = "MIT License",
  url                = "https://bitbucket.org/tshima/lotus_core",
  classifiers        = ["License :: OSI Approved :: MIT License",
                        "Operating System :: MacOS :: MacOS X", 
                        "Operating System :: POSIX :: Linux", 
                       ],
  test_suite         = "test_suite.suite"
)

