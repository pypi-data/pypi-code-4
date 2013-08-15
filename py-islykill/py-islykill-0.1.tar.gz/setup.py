# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import platform

DESCRIPTION = "A simple python client for the Icelandic government authentication service Íslykill (www.islykill.is)"

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open('README.md').read()
except:
    pass

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    name='py-islykill',
    version='0.1',
    author=u'Overcast Software - Sævar Öfjörð Magnússon',
    author_email='saevar@overcast.io',
    py_modules=['islykill'],
    url='http://github.com/overcastsoftware/py-islykill',
    license='MIT',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=CLASSIFIERS,
)
