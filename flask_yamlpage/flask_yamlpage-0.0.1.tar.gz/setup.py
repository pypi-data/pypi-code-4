#!/usr/bin/env python
import os
import sys
import doctest
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

import flask_yamlpage as mod


NAME = mod.__name__
DOC = mod.__doc__.strip()


open('README.md', 'w').write(DOC)
if sys.argv[-1] == 'publish':
    if not doctest.testfile('README.md').failed:
        os.system('python setup.py sdist upload')
        sys.exit(1)

if len(sys.argv) == 1:
    print 'Use "./setup.py register" for registration or update package'
    print 'Or  "./setup.py publish" for publication new release'
    sys.exit()


setup(
    name         = mod.__name__,
    url          = 'https://github.com/imbolc/%s' % mod.__name__,
    version      = mod.__version__,
    description  = DOC.split('===\n')[1].strip().split('\n\n')[0],
    long_description = mod.__doc__.split('\n\n', 1)[1],

    py_modules   = [mod.__name__],

    author       = 'Imbolc',
    author_email = 'imbolc@imbolc.name',
    license      = 'MIT',

    classifiers  = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
    ],

    install_requires=['yamlpage'],
)
