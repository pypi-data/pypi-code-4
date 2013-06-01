#!/usr/bin/env python


from setuptools import setup, find_packages
setup(
    name = "wlnm",
    version = "0.1.0",
    packages = find_packages(),
    

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        #'': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
	'wlst':['./wlst/*.py'],
    },

    # metadata for upload to PyPI
    author = "Kevin Yi",
    author_email = "yikaus A gmail ",
    description = "Weblogic Node Master",
    license = "BSD",
    keywords = "weblogic admin administrator node manage",
    url = "https://github.com/yikaus/wlnm",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.

    entry_points = {
        'console_scripts': [
            'wlnm = wlnm.wlnm:main',
        ],
    }
)