#!/usr/bin/env python
"""
bigsky
=================
WNYC's "bigsky" big data image processing initiative.
"""

from setuptools import setup

setup(
    name='bigsky',
    version='0.0.0',
    author='Adam DePrince',
    author_email='adeprince@nypublicradio.org',
    description="WNYC's big data image processing toolkit",
    long_description=__doc__,
    url="http://github.com/wnyc/bigsky",
    py_modules=[
        'bigsky/__init__',
        'bigsky/inputs/__init__',
        'bigsky/inputs/reader',
        'bigsky/inputs/flickr',
        'bigsky/exif/__init__',
        'bigsky/outputs/__init__',
        'bigsky/outputs/to_googlemap',
        'bigsky/outputs/simpledb_import',
        'bigsky/outputs/simpledb_output',
        'bigsky/outputs/s3_import',
        'bigsky/outputs/exiv2',
        ],
    packages=['bigsky',],
    zip_safe=True,
    license='MIT',
    include_package_data=True,
    classifiers=[],
    scripts=['scripts/bigsky_spider', 'scripts/bigsky_exif', 'scripts/bigsky_html', 'scripts/bigsky_simpledb_import', 'scripts/bigsky_s3_import', 'scripts/bigsky_simpledb_output', 'scripts/bigsky_exiv2'],
    install_requires=[
        'python-gflags',
        'boto>=2.13.0',
        'PIL',
        'flickrapi>=1.4.2',
        'PIL>=1.1.7',
        'wsgiref>=0.1.2',
        ]
    )
