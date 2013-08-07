#!/usr/bin/env python
"""
humbug_forensics
======

Fake hum forensics.

humbug --notchfilter=50|60 --start=<human readable datetime> --intensity=<float> audiofile.wav


Humbug will download power grid frequency data from dagrid.us,
optionally remove existing A/C hum data and apply A/C hum data for a
specific date and time.


"""

from setuptools import setup


setup(
    name='humbug-forensics',
    version='0.0.0',
    author='Adam DePrince',
    author_email='deprince@googlealumni.com',
    description='Simple utility to fake "hum forensics"',
    long_description=__doc__,
    py_modules = [
        "humbug-forensics",
        ],
    packages = [],
    zip_safe=True,
    include_package_data=True,
    classifiers=[
        ],
    scripts = [
        "scripts/humbugger",
        ],
    url = "https://github.com/adamdeprince/humbug_forensics",
    install_requires = [
        'requests',
        'python-gflags',
        'pysox',
        'python-dateutil'
        ]
)

