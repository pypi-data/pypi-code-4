# -*- coding: utf8 -*-
from setuptools import setup

long_description = open("README.rst").read()
setup(
    name="python_vdx",
    version="0.1",
    author = 'Strata Tech Ltd. ( http://stratatech.ru )',
    author_email = 'info@stratatech.ru',    
    url="http://gitlab.stratatech.ru/public/projects/python_vdx/python_vdx",
    
    description="Package for working with MS Visio VDX files",
    long_description = long_description,
    license='LICENSE.txt',
    
    packages=['vdx'],
    package_data={
        "vdx": [
            "shapes/*.xml",
        ]
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Natural Language :: Russian',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',        
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    
    py_modules=['vdx'],    
    install_requires=[
        "beautifulsoup4",
        "lxml",        
    ],  
)
