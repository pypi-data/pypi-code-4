#!/usr/bin/env python

from glob import glob
from os import getcwd, path
from imp import new_module

from setuptools import setup, find_packages


version = new_module("version")

exec(
    compile(open(path.join(path.dirname(globals().get("__file__", path.join(getcwd(), "spyda"))), "spyda/version.py"), "r").read(), "spyda/version.py", "exec"),
    version.__dict__
)


setup(
    name="spyda",
    version=version.version,
    description="Spyda - Python Spider Tool and Library",
    long_description="{0:s}\n\n{1:s}".format(
        open("README.rst").read(), open("CHANGES.rst").read()
    ),
    author="James Mills",
    author_email="James Mills, j dot mills at griffith dot edu dot au",
    url="https://bitbucket.org/prologic/spyda",
    download_url="https://bitbucket.org/prologic/spyda/downloads/",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    license="MIT",
    keywords="Python Spider Web Crawling and Extraction Tool and Library",
    platforms="POSIX",
    packages=find_packages("."),
    scripts=glob("bin/*"),
    dependency_links=[
        "https://bitbucket.org/prologic/calais/get/tip.zip#egg=calais-dev"
    ],
    install_requires=[
        "BeautifulSoup==3.2.1",
        "cssselect==0.8",
        "lxml==3.2.1",
        "nltk==2.0.4",
        "restclient==0.11.0",
        "url==0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "crawl=spyda.crawler:main",
            "extract=spyda.extractor:main",
            "match=spyda.matcher:main"
        ]
    },
    test_suite="tests.main.main",
    zip_safe=True
)
