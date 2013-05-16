# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys
import pkg_resources

sys.path.insert(0, 'src')
import envassert


long_description = open("README.rst").read()

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Topic :: Software Development :: Testing",
    "Topic :: System :: Monitoring",
    "Topic :: System :: Systems Administration",
]

requires = ['fabric']
deplinks = []

setup(
    name='envassert',
    version=envassert.__version__,
    description='Test your servers environments by using fabric.',
    long_description=long_description,
    classifiers=classifiers,
    keywords=['test','server'],
    author='WAKAYAMA Shirou',
    author_email='shirou.faw at gmail.com',
    url='http://bitbucket.org/r_rudi/envassert',
    download_url='http://pypi.python.org/pypi/envassert',
    license='MIT License',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=requires,
    dependency_links=deplinks
)

