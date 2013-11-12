#!/usr/bin/env python
import platform
import sys
from setuptools import setup, find_packages

tf_platform = platform.system()
real_arch = platform.machine().upper()

if(real_arch == "X86_64"):
	tf_arch = "x64"
elif(real_arch == "X86"):
	tf_arch = "x86"
elif(real_arch == "ARML"):
	tf_arch = "ArmL"
elif(real_arch == "ARMHF"):
	tf_arch = "ArmHF"
else:
	tf_arch = "unsupported"

if(platform.python_version()[0] == "2"):
	tf_python_ver = "2X"
else:
	tf_python_ver = "3X"

tf_package = "TransFabric-Python{0}-{1}-{2}".format(tf_python_ver, tf_platform, tf_arch)

setup(
        name = tf_package,
        version = '1.0',
        author      = "TransFabric Ltd",
        description = """TransFabric Parser for Python {0}, for hardware {1}-{2}""".format(tf_python_ver, tf_platform, tf_arch),
 	package_data = {'':['_TransFabric.so']},
        platforms=[""],
        packages=find_packages(),
        classifiers=["Classifier: Development Status :: 2 - Pre-Alpha", 
        "Classifier: License :: Free for non-commercial use",
        "Classifier: Natural Language :: English",
        "Classifier: Topic :: Software Development :: Libraries"]
        )



