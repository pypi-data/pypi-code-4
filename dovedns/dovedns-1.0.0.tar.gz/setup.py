#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "dovedns",
    version = "1.0.0",
    author = "HawkOwl",
    author_email = "hawkowl@outlook.com",
    description = "DoveDNS is a library for interfacing with Linode DNSManager, using Twisted.",
    long_description = "DoveDNS is a library for interfacing with Linode DNSManager, using Twisted.",
    keywords = ["twisted", "linode", "dns"],
    url = "https://github.com/hawkowl/dovedns",
    packages = ['dovedns'],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Framework :: Twisted",
        "Topic :: Internet :: Name Service (DNS)"
    ],
)