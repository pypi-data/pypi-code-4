#!/usr/bin/env python

import os
import sys

import static

version = static.__version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_requirements(filename):
    return list([x.strip() for x in open(filename).readlines()])

if sys.argv[-1] == 'test':
    requirements = get_requirements("requirements_test.txt")
else:
    requirements = get_requirements("requirements.txt")


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read()


setup(
    name='staticserve',
    version=version,
    description='A simple WSGI way to serve static (or mixed) content.',
    long_description=readme + '\n\n' + history,
    author='Daniel Greenfeld',
    author_email='pydanny@gmail.com',
    url='https://github.com/pydanny/staticserve',
    license="LGPL",
    py_modules=['static', ],
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
    keywords='wsgi web http static content webapps',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities'
    ],
    test_suite='tests',
)