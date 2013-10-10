from distutils.core import setup
from setuptools import find_packages

setup(
    name                    =   's3domain',
    version                 =   '1.0.1',
    description             =   'Script for creating a new s3 bucket with webhosting turned on.',
    long_description        =   'See http://dryan.github.io/s3domain for more information.',
    author                  =   'Daniel Ryan',
    author_email            =   'dryan@dryan.com',
    url                     =   'http://dryan.github.io/s3domain',
    license                 =   'MIT License',
    packages                =   find_packages(),
    scripts                 =   ['s3domain.py'],
    zip_safe                =   True,
    include_package_data    =   True,
    install_requires        =   "boto",
    entry_points            =   """[console_scripts]
s3domain = s3domain:main
"""
)
