# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.txt') as file:
    long_description = file.read()

setup(
    name = "torweb",
    version = "0.0.2",
    #packages = find_packages(exclude=["test.*", "test"]),
    packages = ["torweb"],
    include_package_data = True,
    author = "zhangpeng",
    author_email = "zhangpeng1@infohold.com.cn",
    url = "",
    description = "torweb",
    long_description=long_description,
    install_requires=[],
)
