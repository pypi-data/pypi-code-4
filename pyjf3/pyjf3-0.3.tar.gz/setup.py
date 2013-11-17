# -*- coding: utf-8 -*-
import os, sys
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), 
            encoding='utf-8').read()

setup(
    name='pyjf3',
    version='0.3',
    description = 'Japanese text functions for Python 3',
    long_description = read('README.rst'),
    author = 'Atsuo Ishimoto',
    author_email = 'ishimoto@gembook.org',
    url = 'https://github.com/atsuoishimoto/pyjf3',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
    license='MIT License',
    py_modules = ['pyjf3']

)
