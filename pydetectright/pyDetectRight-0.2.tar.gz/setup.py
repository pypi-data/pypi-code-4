import os
import sys
from setuptools import setup
from pyDetectRight import __version__

setup(
    name = "pyDetectRight",
    version = __version__,
    url = 'https://github.com/caesar0301/pyDetectRight',
    author = 'Jamin Chen',
    author_email = 'chenxm35@gmail.com',
    description = 'A Python wrapper for DetectRight Java API.',
    long_description='''A Python wrapper for DetectRight Java API. This wrapper is based on Py4J to communicate with Java library officially provided. For native Java API, please visit http://detectright.com/''',
    license = "LICENSE",
    packages = ['pyDetectRight'],
    package_dir = {'pyDetectRight': 'pyDetectRight'},
    package_data = {'pyDetectRight': ['java/lib/*.jar', 'java/src/omnilab/bd/chenxm/*.java']},
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: Freely Distributable',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries :: Python Modules',
   ],
)