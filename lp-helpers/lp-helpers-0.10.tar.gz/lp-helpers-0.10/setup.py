#!/usr/bin/env python

from setuptools import setup

setup(
    name = "lp-helpers",
    version = '0.10',
    author = "Brendan Donegan",
    author_email = "brendan-donegan@canonical.com",
    license = "GPL",
    description = "Helper scripts for working with Launchpad and Bazaar.",
    long_description = """
This project provides scripts for simplifying common workflows involving Launchpad and Bazaar. More information at https://github.com/brendan-donegan/lp-helpers
""",
    scripts = ["lp-propose-merge","lp-file-bug", "lp-recipe-build"],
    install_requires = ["bzr", "launchpadlib"]
)

