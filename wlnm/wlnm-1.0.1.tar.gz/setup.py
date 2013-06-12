#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "wlnm",
    version = "1.0.1",
    packages = find_packages(),
    
    include_package_data = True,
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        #'': ['*.txt', '*.rst','*.js','*.css','*.html','*.jpg',],
        # And include any *.msg files found in the 'hello' package, too:
        # 'hello': ['*.msg'],
	
    },

    # metadata for upload to PyPI
    author = "Kevin Yi",
    author_email = "yikaus A gmail ",
    description = "Weblogic Node Master",
    license = "BSD",
    keywords = "weblogic admin administrator node manage",
    install_requires=["psutil","bottle","Beaker"],
    url = "https://github.com/yikaus/wlnm",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.

    entry_points = {
        'console_scripts': [
            'wlnm = wlnm.wlnm:main',
	    'wlns = wlnm.wlns:main',
	    'wlna = wlnm.wlna:main',
	    'wlnws = wlnm.wlnws:main',
        ],
    }
)