# -*- coding: utf-8 -*-
"""
This file is part of the charset python package
Copyrighted by Karel Vedecia Ortiz <kverdecia@uci.cu, kverdecia@gmail.com>
License: MPL 2.0 (http://www.mozilla.org/MPL/2.0/)
"""
__author__ = "Karel Antonio Verdecia Ortiz"
__contact__ = "kverdecia@uci.cu, kverdecia@gmail.com"


import glob
from setuptools import setup, find_packages, Extension

detector_src = ['src/charset.detector.cpp'] + glob.glob('src/mozilladetector/*.cpp')


version = '1.0.1'


setup(name='charset',
    version=version,
    description="Clases for charset detection. Uses chardet and mozilla universal charset detection.",
    long_description="""\
""",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Karel Antonio Verdecia Ortiz',
    author_email='kverdecia@uci.cu, kverdecia@gmail.com',
    url='',
    license='MPL 2.0',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'chardet',
    ],
    entry_points = {
        'console_scripts': [
            'charset=charset.cmd:CmdCharset.run',
        ],
        'charset.detectors': [
            'chardet=charset.detector:Detector',
            'mozilla=charset.detector:MozDetector',
            'check=charset.detector:CheckDetector',
        ],
    },
    ext_modules=[
        Extension('charset.detector', detector_src, 
            include_dirs=['src/mozilladetector'], language='c++'),
    ],
    
)
