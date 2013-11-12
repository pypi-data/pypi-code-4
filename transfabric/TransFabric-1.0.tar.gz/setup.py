#!/usr/bin/env python
import platform
import sys
from setuptools import setup, find_packages

tf_platform = platform.system().upper()
tf_arch = platform.machine().upper()
tf_python_ver = platform.python_version()[0]
tf_target = "{0}_{1}_{2}".format(tf_python_ver, tf_platform, tf_arch)

supported_platforms = {
"2_LINUX_X86" : "TransFabric-Python2X-Linux-x86",
"2_LINUX_X86_64" : "TransFabric-Python2X-Linux-x64",
"2_LINUX_ARML" : "TransFabric-Python2X-Linux-ArmL",
"2_LINUX_ARMHF" : "TransFabric-Python2X-Linux-ArmHF",
"2_WINDOWS_X86" : "TransFabric-Python2X-Windows-x86",
"2_WINDOWS_X86_64" : "TransFabric-Python2X-Windows-x64",
"2_DARWIN_X86" : "TransFabric-Python2X-Mac-x86",
"2_DARWIN_X86_64" : "TransFabric-Python2X-Mac-x64"
}


if(supported_platforms.has_key(tf_target)):
	tf_req = supported_platforms[tf_target]

	setup(
		name = 'TransFabric',
		version = '1.0',
		author      = "TransFabric Ltd",
		description = """TransFabric Parser""",
		install_requires=[tf_req],
		platforms=[""],
		packages=find_packages(),
		classifiers=["Classifier: Development Status :: 2 - Pre-Alpha", 
		"Classifier: License :: Free for non-commercial use",
		"Classifier: Natural Language :: English",
		"Classifier: Topic :: Software Development :: Libraries"]
		)

else:
	print("Unfortunately, you are running on an unsupported platform")
	print("Please report this to support@transfabric.com, including the platform spec {0}_{1}_{2}".format(tf_python_ver, tf_platform, tf_arch))




