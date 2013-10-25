#!/usr/bin/env python

from glob import glob
from imp import new_module
from os import getcwd, path


from setuptools import setup, find_packages


version = new_module("version")

exec(
    compile(open(path.join(path.dirname(globals().get("__file__", path.join(getcwd(), "clusterprocessing"))), "clusterprocessing/version.py"), "r").read(), "clusterprocessing/version.py", "exec"),
    version.__dict__
)


setup(
    name="clusterprocessing",
    version=version.version,
    description="TBA",
    long_description="{0:s}\n\n{1:s}".format(
        open("README.rst").read(), open("CHANGES.rst").read()
    ),
    author="James Mills",
    author_email="James Mills, prologic at shortcircuit dot net dot au",
    url="TBA",
    download_url="TBA",
    classifiers=[],
    license="TBA",
    keywords="",
    platforms="POSIX",
    packages=find_packages("."),
    include_package_data=True,
    scripts=glob("bin/*"),
    install_requires=[],
    entry_points={},
    test_suite="tests.main.main",
    zip_safe=True
)
