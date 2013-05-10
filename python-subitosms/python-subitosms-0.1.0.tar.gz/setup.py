# -*- coding: iso-8859-1 -*-

# from distribute_setup import use_setuptools
# use_setuptools()

import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'python-subitosms',
    version = '0.1.0',
    packages = ['subitosms', 'subitosms.test'],
    include_package_data = True,
    license = 'BSD License', # example license
    description = 'APis wrapper to SubitoSMS APIs.',
    long_description = README,
    url = 'https://github.com/simodalla/python-subitosms',
    author = 'Simone Dalla',
    author_email = 'simodalla@gmail.com',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    test_suite='subitosms.test'
    )