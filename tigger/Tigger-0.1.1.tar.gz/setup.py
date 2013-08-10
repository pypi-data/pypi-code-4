#!/usr/bin/env python
from setuptools import setup

setup(
        name="Tigger",
        version="0.1.1",
        license="MIT",
        author="Bit Shift",
        author_email="bitshift@bigmacintosh.net",
        url="https://github.com/bit-shift/tigger",
        description="Command-line tagging tool.",
        long_description="Tigger is a command-line tagging tool written in " +
            "python, intended for tracking tags on files in a form which can " +
            "be transferred with the files while remaining out of sight " +
            "normally (much like git's metadata, except not so clever).",
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Topic :: Utilities",
            ],

        packages=["tigger",],

        entry_points={
            "console_scripts": [
                "tigger = tigger.app:main",
                ],
            },
        )
