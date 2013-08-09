#!/usr/bin/env python

from setuptools import setup

setup(name="lpct",
      version="0.9",
      description="lsprof output which is readable by kcachegrind",
      author="David Allouche, Jp Calderone, Itamar Shtull-Trauring and Johan Dahlin; modified by Peter Waller",
      author_email="p@pwaller.net",
      url="https://github.com/pwaller/lpct",
      py_modules=['lsprofcalltree'],
      entry_points={
      	"console_scripts": [
      		"lpct = lsprofcalltree:main",
      	],
      }
     )
