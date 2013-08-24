from distutils.core import setup
from setuptools import find_packages

setup(
    name                    =   'rackup',
    version                 =   '1.0.1',
    description             =   'Script for uploading files to Rackspace Cloud Files',
    long_description        =   'See http://dryan.github.io/rackup for more information.',
    author                  =   'Daniel Ryan',
    author_email            =   'dryan@dryan.com',
    url                     =   'http://dryan.github.io/rackup',
    license                 =   'MIT License',
    packages                =   find_packages(exclude=["r","a","c","k","u","p"]),
    zip_safe                =   True,
    include_package_data    =   True,
    install_requires        =   "pyrax",
    entry_points            =   """[console_scripts]
rackup = rackup.rackup:main
"""
)
