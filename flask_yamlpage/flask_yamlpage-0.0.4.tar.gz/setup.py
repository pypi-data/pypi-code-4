#!/usr/bin/env python
import os
import sys
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup


NAME = 'flask_yamlpage'
try:
    README = open('README.md').read()
except IOError:
    README = ''

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit(1)

if len(sys.argv) == 1:
    print 'Use "./setup.py register" for registration or update package'
    print 'Or  "./setup.py publish" for publication new release'
    sys.exit()


setup(
    name         = NAME,
    url          = 'https://github.com/imbolc/%s' % NAME.replace('_', '-'),
    version      = '0.0.4',
    description  = README.split('===\n')[-1].strip().split('\n\n')[0],
    long_description = README.split('\n\n', 1)[-1],

    py_modules   = [NAME],

    author       = 'Imbolc',
    author_email = 'imbolc@imbolc.name',
    license      = 'MIT',

    classifiers  = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
    ],

    install_requires=['flask', 'yamlpage'],
)
