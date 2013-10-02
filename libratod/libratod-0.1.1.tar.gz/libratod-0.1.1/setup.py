#!/usr/bin/env python
from setuptools import setup

required = [
    'librato-metrics',
    'psutil',
]

setup(
    name="libratod",
    version='0.1.1',
    description="Simple daemon to send stats to librato metrics.",
    scripts=['libratod'],
    author="Aaron Fay",
    author_email="aaron.j.fay@gmail.com",
    packages = [],
    install_requires=required,
)
