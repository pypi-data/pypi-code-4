#!/usr/bin/env python

from distutils.core import setup
import os

if os.path.isfile("/usr/lib/python3.3/site-packages/nanotest.py"):
    os.remove("/usr/lib/python3.3/site-packages/nanotest.py")
elif os.path.isfile("/usr/lib/python3.2/site-packages/nanotest.py"):
    os.remove("/usr/lib/python3.2/site-packages/nanotest.py")
elif os.path.isfile("/usr/lib/python2.7/site-packages/nanotest.py"):
    os.remove("/usr/lib/python2.7/site-packages/nanotest.py")

setup( name = "nanotest",
       version = "2.1.0",
       description = "Tiny testing toolkit (for Python)",
       author = "Shawn Boyette",
       author_email = "shawn@firepear.net",
       url = "https://github.com/firepear/nanotest-py",
       packages = [ "nanotest" ],
       scripts = ['bin/nanotest-py'],
       classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ]
)
