#!/usr/bin/env python

from glob import glob
from os.path import abspath, dirname, join

from setuptools import find_packages, setup


path = abspath(dirname(__file__))
try:
    README = open(join(path, "README.rst")).read()
    RELEASE = open(join(path, "RELEASE.rst")).read()
except IOError:
    README = RELEASE = ""


setup(
    name="passweb",
    version="0.0.1",
    description="Secure Password (Web) Manager",
    long_description="%s\n\n%s" % (README, RELEASE),
    author="James Mills",
    author_email="James Mills, prologic at shortcircuit dot net dot au",
    url="TBA",
    download_url="TBA",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"],
    license="MIT",
    keywords="gpg secure password web manager application",
    platforms="POSIX",
    packages=find_packages("."),
    scripts=glob("bin/*"),
    entry_points="""
    [console_scripts]
    passweb = passweb.main:main
    """,
    install_requires=[
        "yota",
        "jinja2",
        "circuits",
    ],
    zip_safe=False,
    test_suite="tests.main.main"
)
